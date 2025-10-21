from contextvars import ContextVar
from typing import Annotated, Any, Dict, Generic, Optional, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class Edge(BaseModel, Generic[T]):
    edge_type: T
    value: Optional[Any] = None
    source_node: Optional["Node"] = None
    target_node: Optional["Node"] = None
    idx: Annotated[int, Field(ge=0)] = 0
    model_config = ConfigDict(arbitrary_types_allowed=True)


class Node:
    _instance_counts: ContextVar[Dict] = ContextVar("instance_counts", default={})

    @classmethod
    def _get_instance_counts(cls):
        return cls._instance_counts.get()

    def __init__(self):
        # Initialize instance variables
        self._dependencies: list[Edge] = []
        self._node_args: Dict[str, Any] = {}
        self._output_order: Dict[str, int] = {}
        self._node_name: str | None = None
        self._type_name: str | None = None

        cls = self.__class__
        instance_counts = self._get_instance_counts()
        if cls not in instance_counts:
            instance_counts[cls] = 0
        instance_counts[cls] += 1

        self._node_name = f"{cls.__name__}_{instance_counts[cls]}"

    def _add_dependency(self, dependency: Edge):
        self._dependencies.append(dependency)

    def _remove_dependency(self, dependency: Edge):
        self._dependencies.remove(dependency)

    def _get_dependencies(self):
        return self._dependencies

    def _process_inputs(self, **kwargs):
        for key, value in kwargs.items():
            # if value is an Edge, then add it to dependencies
            if isinstance(value, Edge):
                value.target_node = self
                if value.source_node:
                    self._add_dependency(value)
                    self._node_args[key] = value
            else:
                self._node_args[key] = value

    def build_json_workflow(self, node_dict: Dict[str, Any] | None = None):
        if node_dict is None:
            node_dict = {}
        # convert the current node to a json dict
        node_dict[self._node_name] = {}
        node_dict[self._node_name]["inputs"] = {}
        node_dict[self._node_name]["class_type"] = self._type_name
        node_dict[self._node_name]["_meta"] = {}
        node_dict[self._node_name]["_meta"]["title"] = self._node_name
        for arg in self._node_args:
            if isinstance(self._node_args[arg], Edge):
                node_dict[self._node_name]["inputs"][arg] = [
                    self._node_args[arg].source_node._node_name,
                    self._node_args[arg].idx,
                ]
            else:
                if self._node_args[arg] is not None:
                    node_dict[self._node_name]["inputs"][arg] = self._node_args[arg]

        # recursive call to all the dependencies
        for dependency in self._dependencies:
            if dependency and dependency.source_node:
                node_dict = dependency.source_node.build_json_workflow(node_dict)

        # reset instance counts for the current context
        self._get_instance_counts().clear()

        return node_dict
