import logging
import sys
import time
import typing
import traceback

import pydantic
import jsonschema
from mcp.server.fastmcp import FastMCP
from mcp.types import Resource

from jotsu.mcp.types import Workflow
from jotsu.mcp.local import LocalMCPClient
from jotsu.mcp.client.client import MCPClient
from jotsu.mcp.types.models import WorkflowNode, WorkflowModelUsage, WorkflowData, slug

from .handler import WorkflowHandler, WorkflowHandlerResult
from .sessions import WorkflowSessionManager


logger = logging.getLogger(__name__)


class _WorkflowCompleteException(Exception):
    ...


class _WorkflowRef(pydantic.BaseModel):
    id: str
    name: str


class _WorkflowNodeRef(_WorkflowRef):
    type: str

    @classmethod
    def from_node(cls, node: WorkflowNode):
        return cls(id=node.id, name=node.name, type=node.type)


class _WorkflowTracebackFrame(pydantic.BaseModel):
    filename: str
    lineno: int
    func_name: str
    text: str


class WorkflowAction(pydantic.BaseModel):
    action: str
    timestamp: float = 0
    id: typing.Annotated[str, 'The id of this action instance'] = pydantic.Field(default_factory=slug)
    run_id: typing.Annotated[str, 'The id of this run instance']

    @pydantic.model_validator(mode='before')  # noqa
    @classmethod
    def set_defaults(cls, values):
        if values.get('timestamp') is None:
            values['timestamp'] = time.time()
        return values


class WorkflowActionStart(WorkflowAction):
    action: typing.Literal['workflow-start'] = 'workflow-start'
    workflow: _WorkflowRef
    data: WorkflowData = None


class WorkflowActionSchemaError(WorkflowAction):
    action: typing.Literal['schema-error'] = 'workflow-schema-error'
    workflow: _WorkflowRef
    message: str
    exc_type: str
    traceback: typing.List[_WorkflowTracebackFrame]


class WorkflowActionEnd(WorkflowAction):
    action: typing.Literal['workflow-end'] = 'workflow-end'
    workflow: _WorkflowRef
    duration: float
    usage: list[WorkflowModelUsage]


class WorkflowActionFailed(WorkflowAction):
    action: typing.Literal['workflow-failed'] = 'workflow-failed'
    workflow: _WorkflowRef
    duration: float
    usage: list[WorkflowModelUsage]


class WorkflowActionNodeStart(WorkflowAction):
    action: typing.Literal['node-start'] = 'node-start'
    node: _WorkflowNodeRef
    data: WorkflowData


class WorkflowActionNode(WorkflowAction):
    action: typing.Literal['node-end'] = 'node'
    node: _WorkflowNodeRef
    data: WorkflowData
    results: typing.List[WorkflowHandlerResult]
    duration: float


# Keep old name too.
WorkflowActionNodeEnd = WorkflowActionNode


class WorkflowActionNodeError(WorkflowAction):
    action: typing.Literal['node-error'] = 'node-error'
    node: _WorkflowNodeRef
    message: str
    exc_type: str
    traceback: typing.List[_WorkflowTracebackFrame]


class WorkflowActionDefault(WorkflowAction):
    action: typing.Literal['default'] = 'default'
    node: _WorkflowNodeRef
    data: dict


class WorkflowEngine(FastMCP):
    MOCKS = '__mocks__'
    MOCK_TYPE = '__type__'

    def __init__(
            self, workflows: Workflow | typing.List[Workflow], *args,
            client: typing.Optional[MCPClient] = None, handler_cls: typing.Type[WorkflowHandler] = None,
            **kwargs
    ):
        self._workflows = [workflows] if isinstance(workflows, Workflow) else workflows
        self._client = client if client else LocalMCPClient()
        self._handler = handler_cls(self) if handler_cls is not None else WorkflowHandler(engine=self)

        super().__init__(*args, **kwargs)
        self.add_tool(self.run_workflow, name='workflow')

        for workflow in self._workflows:
            name = workflow.name if workflow.name else workflow.id
            resource = Resource(
                name=name,
                description=workflow.description,
                uri=pydantic.AnyUrl(f'workflow://{workflow.id}/'),
                mimeType='application/json'
            )
            self.add_resource(resource)

    @property
    def handler(self) -> WorkflowHandler:
        return self._handler

    def _get_workflow(self, name: str) -> Workflow | None:
        for workflow in self._workflows:
            if workflow.id == name:
                return workflow
        for workflow in self._workflows:
            if workflow.name == name:
                return workflow
        return None

    @staticmethod
    def _get_tb(tb):
        for frame in traceback.extract_tb(tb, 64):
            yield _WorkflowTracebackFrame(
                filename=frame.filename, lineno=frame.lineno, func_name=frame.name, text=frame.line
            )

    @staticmethod
    def _results(
            node: WorkflowNode, values: dict | typing.List[WorkflowHandlerResult]
    ) -> typing.List[WorkflowHandlerResult]:
        return [WorkflowHandlerResult(edge=edge, data=values) for edge in node.edges] \
            if isinstance(values, dict) else values

    async def _run_workflow_node(
            self, workflow: Workflow, node: WorkflowNode, data: dict, *,
            nodes: typing.Dict[str, WorkflowNode], sessions: WorkflowSessionManager, usage: list[WorkflowModelUsage],
            run_id: str, mocks: typing.Dict[str, dict]
    ):
        ref = _WorkflowNodeRef.from_node(node)

        action_id = slug()
        method = getattr(self._handler, f'handle_{node.type}', None)
        if method:
            start = time.time()
            yield WorkflowActionNodeStart(
                node=ref, data=data, run_id=run_id, timestamp=start
            ).model_dump()

            try:
                if node.id not in mocks:
                    result = await method(
                        data, action_id=action_id, workflow=workflow, node=node, sessions=sessions, usage=usage
                    )
                else:
                    # Mocks/testing
                    mock = mocks[node.id].copy()
                    mock_type = mock.pop(self.MOCK_TYPE, '')
                    if mock_type.lower() == 'replace':
                        result = mock
                    else:
                        result = data | mock
                results: typing.List[WorkflowHandlerResult] = self._results(node, result)

                end = time.time()
                yield WorkflowActionNode(
                    id=action_id, node=ref, data=data, results=results, run_id=run_id,
                    timestamp=end, duration=end - start
                ).model_dump()
            except Exception as e:  # noqa
                logger.exception('handler exception')

                # If there is only one exception in the group, return that instead.
                if isinstance(e, ExceptionGroup):
                    group = typing.cast(ExceptionGroup, e)
                    if len(group.exceptions) == 1:
                        e = group.exceptions[0]

                exc_type = type(e)
                tb = e.__traceback__

                yield WorkflowActionNodeError(
                    node=ref, message=str(e), run_id=run_id,
                    exc_type=exc_type.__name__, traceback=list(self._get_tb(tb))
                ).model_dump()

                raise e

        else:
            # result and complete don't have handlers.
            yield WorkflowActionNode(
                id=action_id, node=ref, data=data, results=[], run_id=run_id,
                timestamp=time.time(), duration=0
            ).model_dump()

            if node.type == 'complete':
                raise _WorkflowCompleteException(data)

            results: typing.List[WorkflowHandlerResult] = self._results(node, data)

        for result in results:
            node = nodes[result.edge]
            async for status in self._run_workflow_node(
                    workflow, node, result.data, nodes=nodes,
                    sessions=sessions, usage=usage, run_id=run_id, mocks=mocks
            ):
                yield status

    async def get_workflow(self, name: str):
        return self._get_workflow(name)

    async def run_workflow(self, name: str, data: dict = None, *, run_id: str = None):
        start = time.time()
        usage: list[WorkflowModelUsage] = []

        workflow = await self.get_workflow(name)
        if not workflow:
            logger.error('Workflow not found: %s', name)
            raise ValueError(f'Workflow not found: {name}')

        run_id = run_id if run_id else slug()
        workflow_name = f'{workflow.name} [{workflow.id}]' if workflow.name != workflow.id else workflow.name
        logger.info("Running workflow '%s'.", workflow_name)

        payload = workflow.data.copy() if workflow.data else {}
        if data:
            payload.update(data)

        mocks = payload.pop(self.MOCKS, {})

        ref = _WorkflowRef(id=workflow.id, name=workflow.name or workflow.id)
        yield WorkflowActionStart(workflow=ref, timestamp=start, data=payload, run_id=run_id).model_dump()

        if workflow.event and workflow.event.json_schema:
            try:
                jsonschema.validate(instance=payload, schema=workflow.event.json_schema)
            except jsonschema.ValidationError as e:
                exc_type, _, tb = sys.exc_info()
                yield WorkflowActionSchemaError(
                    workflow=ref, message=str(e), run_id=run_id,
                    exc_type=exc_type.__name__, traceback=list(self._get_tb(tb)),
                ).model_dump()

                end = time.time()
                duration = end - start
                yield WorkflowActionFailed(
                    workflow=ref, timestamp=end, duration=duration, usage=usage, run_id=run_id
                ).model_dump()
                logger.info(
                    "Workflow '%s' failed due to invalid schema in %s seconds.",
                    workflow_name, f'{duration:.4f}'
                )
                return

        nodes = {node.id: node for node in workflow.nodes}
        node = nodes.get(workflow.start_node_id)

        if not node:
            end = time.time()
            duration = end - start

            yield WorkflowActionEnd(
                workflow=ref, timestamp=end, duration=duration, usage=usage, run_id=run_id
            ).model_dump()

            logger.info(
                "Empty workflow '%s' completed successfully in %s seconds.",
                workflow_name, f'{end - start:.4f}'
            )
            return

        sessions = WorkflowSessionManager(workflow, client=self._client)
        try:
            success = True
            try:
                async for status in self._run_workflow_node(
                        workflow, node, data=payload, nodes=nodes,
                        sessions=sessions, usage=usage, run_id=run_id, mocks=mocks,
                ):
                    # check for result
                    yield status
            except _WorkflowCompleteException:
                pass
            except:  # noqa
                success = False

            end = time.time()
            duration = end - start

            if success:
                yield WorkflowActionEnd(
                    workflow=ref, timestamp=end, duration=duration, usage=usage, run_id=run_id
                ).model_dump()
                logger.info(
                    "Workflow '%s' completed successfully in %s seconds.",
                    workflow_name, f'{duration:.4f}'
                )
            else:
                yield WorkflowActionFailed(
                    workflow=ref, timestamp=end, duration=duration, usage=usage, run_id=run_id
                ).model_dump()
                logger.info(
                    "Workflow '%s' failed in %s seconds.",
                    workflow_name, f'{duration:.4f}'
                )
        finally:
            await sessions.close()
