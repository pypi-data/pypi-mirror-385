from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any, Dict, List, Set, Union

import requests

COMFY_SERVER_ADDRESS = "http://127.0.0.1:8188/"


def read_json_file(filename: str) -> Dict[str, Any]:
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)


def filter_comfy_type(comfy_type: Union[str, List[str]]) -> str:
    if isinstance(comfy_type, list) or any(char in comfy_type for char in "*:/"):
        return "Any"
    return (
        comfy_type.replace(" ", "_")
        .replace("-", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace(",", "")
    )


def filter_var_name(var_name: str) -> str:
    return (
        var_name.replace(" ", "_")
        .replace("-", "_")
        .replace("(", "")
        .replace(")", "")
        .replace(".", "")
        .replace(",", "")
        .replace("|", "_s")
        .replace("*", "Wildcard")
        .replace("+", "")
        .replace(":", "")
        .replace("/", "")
    )


@dataclass
class NodeOutput:
    name: str
    raw_type: Any
    type: str
    is_list: bool

    def __init__(self, name: str, type: Any, is_list: bool):
        self.name = filter_var_name(name)
        self.raw_type = type
        self.type = filter_comfy_type(type)
        self.is_list = is_list


@dataclass
class NodeInput:
    name: str
    raw_type: Any
    type: str
    is_required: bool
    is_hidden: bool

    def __init__(
        self, name: str, type: Any, is_required: bool = True, is_hidden: bool = False
    ):
        self.name = filter_var_name(name)
        self.raw_type = type
        self.type = filter_comfy_type(type)
        self.is_required = is_required
        self.is_hidden = is_hidden


@dataclass
class Node:
    raw_name: str
    name: str
    display_name: str
    description: str
    category: str
    output_node: bool
    inputs: List[NodeInput]
    outputs: List[NodeOutput]


def generate_placeholder_classes(types: Set[str]) -> str:
    return "\n".join([f"class {t}: pass" for t in types])


def get_type_annotation(raw_type: Any) -> str:
    if isinstance(raw_type, list):
        return "Any"
    elif raw_type == "*":
        return "Any"
    else:
        return str(raw_type)


def convert_node_to_py_class(node: Dict[str, Any]) -> Node:
    class_name = node["name"]
    inputs = extract_inputs(node["input"])
    outputs = extract_outputs(
        node["output"], node["output_is_list"], node["output_name"], class_name
    )
    return Node(
        class_name,
        filter_var_name(class_name),
        node["display_name"],
        node["description"],
        node["category"],
        node["output_node"],
        inputs,
        outputs,
    )


def extract_inputs(input_info: Dict[str, Dict[str, List[Any]]]) -> List[NodeInput]:
    inputs = []
    for input_type, type_dict in input_info.items():
        for name, type_list in type_dict.items():
            inputs.append(
                NodeInput(
                    name,
                    type_list[0],
                    is_required=(input_type == "required"),
                    is_hidden=(input_type == "hidden"),
                )
            )
    return inputs


def extract_outputs(
    output_types: List[str],
    output_is_list: List[bool],
    output_name: List[str],
    class_name: str,
) -> List[NodeOutput]:
    outputs = []
    for i, output_type in enumerate(output_types):
        output_name_i = (
            output_name[i]
            if i < len(output_name)
            else f"{class_name}_output_{output_type}"
        )
        outputs.append(NodeOutput(output_name_i, output_type, output_is_list[i]))
    return outputs


def convert_nodes_to_py_classes(nodes_info: Dict[str, Any], output_file: str):
    nodes: List[Node] = []
    all_types: Set[str] = set()
    defined_types: Set[str] = set()

    for node in nodes_info.values():
        node_obj = convert_node_to_py_class(node)
        excluded_names = [
            "KSamplerVariationsStochastic",
            "KSamplerVariationsWithNoise",
            "SimpleMath",
            "MathExpression_spysssss",
        ]
        if node_obj.name not in excluded_names and node_obj.name not in defined_types:
            nodes.append(node_obj)
            all_types.update(input.type for input in node_obj.inputs)
            all_types.update(output.type for output in node_obj.outputs)
            defined_types.add(node_obj.name)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("from __future__ import annotations\n")
        f.write("from typing import Any, Union, List, Tuple, Optional\n")
        f.write("from .models import Edge, Node\n\n")

        undefined_types = all_types - defined_types - {"Any", "Union", "List"}
        f.write(generate_placeholder_classes(undefined_types))
        f.write("\n\n")

        # Avoid parameter/type name collisions by reserving all known type and class names
        reserved_type_names = (
            set(all_types)
            | set(defined_types)
            | {"Any", "Union", "List", "Tuple", "Optional", "Edge", "Node"}
        )

        for node in nodes:
            class_description = f'"""\n\t\t{node.description}\n'
            class_description += f"\t\tCategory: {node.category}\n"
            class_description += f"\t\tOutput Node: {node.output_node}\n"
            class_description += "\t\tInputs:\n"
            for input in node.inputs:
                class_description += f"\t\t  - {input.name}: {input.raw_type}\n"
            class_description += "\n\t\tOutputs:\n"
            for output in node.outputs:
                class_description += f"\t\t  - {output.name}: {output.raw_type}\n"
            class_description += '\n\t"""'

            underscore_class_name = f"_{node.name}"
            f.write(f"class {underscore_class_name}(Node):\n")
            f.write(f"    {class_description}\n\n")

            input_params = []
            param_var_names: List[str] = []
            for input in node.inputs:
                # Use sanitized type for annotations to avoid nested/invalid generics
                type_annotation = (
                    input.type if input.type else get_type_annotation(input.raw_type)
                )
                default = "" if input.is_required and not input.is_hidden else " = None"
                param_name = input.name
                if param_name in reserved_type_names:
                    param_name = f"{param_name}_input"
                input_params.append(
                    f"{param_name}: Edge[{type_annotation}] | Any{default}"
                )
                param_var_names.append(param_name)

            f.write(f"    def __init__(self, {', '.join(input_params)}):\n")
            for idx, input in enumerate(node.inputs):
                f.write(f"        self.{input.name} = {param_var_names[idx]}\n")
            for idx, output in enumerate(node.outputs):
                # Use sanitized type for annotations to avoid nested/invalid generics
                type_annotation = (
                    output.type if output.type else get_type_annotation(output.raw_type)
                )
                # For Any type, don't add parentheses as it's not instantiable
                edge_type_value = (
                    f"{type_annotation}"
                    if type_annotation == "Any"
                    else f"{type_annotation}()"
                )
                f.write(
                    f"        self.out_{output.name}: Edge[{type_annotation}] = Edge[{type_annotation}](edge_type={edge_type_value}, source_node=self, target_node=None, idx={idx})\n"
                )
            f.write("        super().__init__()\n")
            f.write(f"        self._type_name = '{node.raw_name}'\n")
            f.write(
                "        self._process_inputs(**{k: v for k, v in self.__dict__.items() if not k.startswith('_') and not k.startswith('out_')})\n"
            )

            if len(node.outputs) == 1:
                rt = (
                    node.outputs[0].type
                    if node.outputs[0].type
                    else get_type_annotation(node.outputs[0].raw_type)
                )
                return_type = f"Edge[{rt}]"
            elif len(node.outputs) > 1:
                return_types = []
                for output in node.outputs:
                    ot = (
                        output.type
                        if output.type
                        else get_type_annotation(output.raw_type)
                    )
                    return_types.append(f"Edge[{ot}]")
                return_type = f"Tuple[{', '.join(return_types)}]"
            else:
                return_type = "None"

            f.write(f"\n    def __call__(self) -> {return_type}:\n")
            if len(node.outputs) == 1:
                f.write(f"        return self.out_{node.outputs[0].name}\n")
            elif len(node.outputs) > 1:
                f.write(
                    f"        return ({', '.join([f'self.out_{output.name}' for output in node.outputs])})\n"
                )
            else:
                f.write("        return None\n")
            f.write("\n")

            # Emit public function wrapper with original name, returning outputs directly
            # For output nodes, return the node instance (to allow methods like build_json_workflow())
            params_sig = ", ".join(input_params)
            wrapper_return_type = (
                underscore_class_name if node.output_node else return_type
            )
            f.write(f"def {node.name}({params_sig}) -> {wrapper_return_type}:\n")
            f.write(
                f"    _node = {underscore_class_name}({', '.join(param_var_names)})\n"
            )
            if node.output_node:
                f.write("    return _node\n\n")
            else:
                f.write("    return _node.__call__()\n\n")


if __name__ == "__main__":
    # if comfy address given as an argument, use it
    if len(sys.argv) > 1:
        addr = sys.argv[1]
        COMFY_SERVER_ADDRESS = addr if addr.endswith("/") else addr + "/"

    # Get the nodes info from the comfy server
    response = requests.get(f"{COMFY_SERVER_ADDRESS}object_info")
    nodes_info = response.json()

    # Convert the nodes info to python classes
    convert_nodes_to_py_classes(nodes_info, "nodes.py")
