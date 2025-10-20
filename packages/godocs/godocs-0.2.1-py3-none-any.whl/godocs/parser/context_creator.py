from typing import TypedDict
from .xml_parser import (
    XMLNode,
    XMLDoc,
)
from godocs.translation.translator import SyntaxTranslator
from godocs.translation.interpreter import Interpreter


class Property(TypedDict):
    name: str
    type: str
    default: str
    description: str


class Constant(TypedDict):
    name: str
    value: str
    description: str


class Method(TypedDict):
    name: str
    type: str
    args: list[Property]
    description: str


class Signal(TypedDict):
    name: str
    args: list[Property]
    description: str


class Enum(TypedDict):
    name: str
    values: list[Constant]
    description: str


class ThemeItem(TypedDict):
    name: str
    data_type: str
    type: str
    default: str
    description: str


class Class(TypedDict):
    name: str
    inheritage: list[str]
    brief_description: str
    description: str
    properties: list[Property]
    methods: list[Method]
    signals: list[Signal]
    constants: list[Constant]
    enums: list[Enum]
    theme_items: list[ThemeItem]


class DocContext(TypedDict):
    classes: list[Class]
    options: dict[str, str]


def get_class_node(class_name: str, docs: list[XMLDoc]) -> XMLNode | None:
    for doc in docs:
        root = doc.getroot()

        if root.attrib.get("name") == class_name:
            return root

    return None


def parse_inheritage(root: XMLNode, docs: list[XMLDoc]) -> list[str]:
    result: list[str] = []

    parent_name = root.attrib.get("inherits", '')

    while parent_name != '':
        result.append(parent_name)

        parent = get_class_node(parent_name, docs)

        if parent is None:
            break

        parent_name = parent.attrib.get("inherits", '')

    return result


def parse_property(node: XMLNode) -> Property:
    """
    Parses a member node into a dict.

    Member node structure::

        <member name="color" type="Color" setter="set_color" getter="get_color" default="null">
          Description
        </member>

    Return structure::

        result = {
            "name": "color",
            "type": "Color",
            "default": "null",
            "description": "Description",
        }
    """

    result: Property = {
        "name": '',
        "type": '',
        "default": '',
        "description": '',
    }

    result["name"] = node.attrib.get("name", '')
    result["type"] = node.attrib.get("type", '')
    result["default"] = node.attrib.get("default", '')
    result["description"] = node.text.strip() if node.text is not None else ''

    return result


def parse_method(node: XMLNode) -> Method:
    """
    Parses a method node into a dict.

    Method node structure::

        <method name="add">
          <return type="int" />
          <param index="0" name="num1" type="int" />
          <param index="1" name="num2" type="int" />
          <description>
            Description
          </description>
        </method>

    Return structure::

        result = {
          "name": "add",
          "type": "int",
          "args": [
            {
              "name": "num1",
              "type": "int",
              "default": "",
              "description": "",
            },
            {
              "name": "num2",
              "type": "int",
              "default": "",
              "description": "",
            },
          ],
          "description": "Description",
        }
    """

    result: Method = {
        "name": '',
        "type": '',
        "args": [],
        "description": '',
    }

    result["name"] = node.attrib.get("name", '')
    result["type"] = node.find("return").attrib.get("type", '')  # type: ignore
    result["description"] = node \
        .find("description") \
        .text.strip() if node.text is not None else ''  # type: ignore

    for arg in node.findall("param"):
        result["args"].append(parse_property(arg))

    return result


def parse_signal(node: XMLNode) -> Signal:
    """
    Parses a signal node into a dict.

    Signal node structure::

        <signal name="damaged">
          <param index="0" name="amount" type="float" />
          <description>
            Emitted when someone gets damaged.
          </description>
        </signal>

    Return structure::

        result = {
          "name": "damaged",
          "args": [
            {
              "name": "amount",
              "type": "float",
              "default": "",
              "description": "",
            },
          ],
          "description": "Emitted when someone gets damaged.",
        }
    """

    result: Signal = {
        "name": '',
        "args": [],
        "description": '',
    }

    result["name"] = node.attrib.get("name", '')
    result["description"] = node \
        .find("description") \
        .text.strip() if node.text is not None else ''  # type: ignore

    for arg in node.findall("param"):
        result["args"].append(parse_property(arg))

    return result


def parse_constant(node: XMLNode) -> Constant:
    """
    Parses a constant node into a dict.

    Constant node structure::

        <constant name="PI" value="3.14">
          The value of PI.
        </constant>

    Return structure::

        result = {
          "name": "PI",
          "value": 3.14,
          "description": "The value of PI.",
        }
    """

    result: Constant = {
        "name": '',
        "value": '',
        "description": '',
    }

    result["name"] = node.attrib.get("name", '')
    result["value"] = node.attrib.get("value", '')
    result["description"] = node.text.strip() if node.text is not None else ''

    return result


def parse_enum(name: str, values: list[XMLNode]) -> Enum:
    """
    Parses a list of constant nodes into an enum dict.

    Different from the other parse functions, this one accepts a
    name and a list of XMLNodes with the enum constants.

    This is done this way because the Godot XML docs don't
    treat enums as a separate "entity". Enum members are got from
    constants with a enum attribute in common, which defines the
    name from the enum.

    Also because of the XML docs structure, Enums don't store
    description data, which is why this function's enum dict
    will always have an empty str as its description.

    node structure::

        <constant name="ADDITION" value="0" enum="Operation">
          Operation of adding two numbers.
        </constant>
        <constant name="SUBTRACTION" value="1" enum="Operation">
          Operation of subtracting two numbers.
        </constant>

    Return structure::

        result = {
          "name": "Operation",
          "values": [
            {
              "name": "ADDITION",
              "value": "0",
              "description": "Operation of adding two numbers.",
            },
            {
              "name": "SUBTRACTION",
              "value": "1",
              "description": "Operation of subtracting two numbers.",
            },
          ],
          "description": "",
        }
    """

    result: Enum = {
        "name": '',
        "values": [],
        "description": '',
    }

    result["name"] = name

    for value in values:
        result["values"].append(parse_constant(value))

    # result["description"] =  There's no way to get enum descriptions with doctool

    return result


def parse_theme_item(node: XMLNode) -> ThemeItem:
    result: ThemeItem = {
        "name": '',
        "data_type": '',
        "type": '',
        "default": '',
        "description": '',
    }

    result["name"] = node.attrib.get("name", '')
    result["data_type"] = node.attrib.get("data_type", '')
    result["type"] = node.attrib.get("type", '')
    result["default"] = node.attrib.get("default", '')
    result["description"] = node.text.strip() if node.text is not None else ''

    return result


def parse_properties(node: XMLNode) -> list[Property]:
    """
    Parses a node with a list of properties into a dict.

    Properties node structure::

        <members>
          <member name="color" type="Color" setter="set_color" getter="get_color" default="null">
            A thinga with color and name.
          </member>
          <member name="name" type="String" setter="set_name" getter="get_name" default="null">
            The name of the thinga.
          </member>
        </members>

    Return structure::

        result = [
          {
            "name": "color",
            "type": "Color",
            "default": "null",
            "description": "A thinga with color and name.",
          },
          {
            "name": "name",
            "type": "String",
            "default": "null",
            "description": "The name of the thinga.",
          },
        ]
    """

    result: list[Property] = []

    for property in node:
        if property.text is None or property.text.strip() == '':
            continue

        result.append(parse_property(property))

    return result


def parse_methods(node: XMLNode) -> list[Method]:
    """
    Parses a node with a list of methods into a list of dicts.

    Methods node structure::

        <methods>
          <method name="add">
            <return type="int" />
            <param index="0" name="num1" type="int" />
            <param index="1" name="num2" type="int" />
            <description>
              Adds two numbers.
            </description>
          </method>
          <method name="subtract">
            <return type="int" />
            <param index="0" name="num1" type="int" />
            <param index="1" name="num2" type="int" />
            <description>
              Subtracts the second number from the first.
            </description>
          </method>
        </methods>

    Return structure::

        result = [
          {
            "name": "add",
            "type": "int",
            "args": [
              {"name": "num1", "type": "int", "default": "", "description": ""},
              {"name": "num2", "type": "int", "default": "", "description": ""},
            ],
            "description": "Adds two numbers.",
          },
          {
            "name": "subtract",
            "type": "int",
            "args": [
              {"name": "num1", "type": "int", "default": "", "description": ""},
              {"name": "num2", "type": "int", "default": "", "description": ""},
            ],
            "description": "Subtracts the second number from the first.",
          },
        ]
    """

    result: list[Method] = []

    for method in node.findall("method"):
        description = method.find("description").text  # type: ignore

        if description is None or description.strip() == '':
            continue

        result.append(parse_method(method))

    return result


def parse_signals(node: XMLNode) -> list[Signal]:
    """
    Parses a node with a list of signals into a list of dicts.

    Signals node structure::

        <signals>
          <signal name="damaged">
            <param index="0" name="amount" type="float" />
            <description>
              Emitted when someone gets damaged.
            </description>
          </signal>
          <signal name="healed">
            <param index="0" name="amount" type="float" />
            <description>
              Emitted when someone gets healed.
            </description>
          </signal>
        </signals>

    Return structure::

        result = [
          {
            "name": "damaged",
            "args": [
              {"name": "amount", "type": "float", "default": "", "description": ""},
            ],
            "description": "Emitted when someone gets damaged.",
          },
          {
            "name": "healed",
            "args": [
              {"name": "amount", "type": "float", "default": "", "description": ""},
            ],
            "description": "Emitted when someone gets healed.",
          },
        ]
    """

    result: list[Signal] = []

    for signal in node.findall("signal"):
        description = signal.find("description").text  # type: ignore

        if description is None or description.strip() == '':
            continue

        result.append(parse_signal(signal))

    return result


def parse_constants(node: XMLNode) -> list[Constant]:
    """
    Parses a node with a list of constants into a list of dicts.

    This function ignores the constants that have an enum attribute,
    which would make them members of an Enum.

    For getting members of an Enum, the parse_enums function should be used.

    Constants node structure::

        <constants>
          <constant name="PI" value="3.14">
            The value of PI.
          </constant>
          <constant name="E" value="2.71">
            The value of Euler's number.
          </constant>
        </constants>

    Return structure::

        result = [
          {
            "name": "PI",
            "value": "3.14",
            "description": "The value of PI.",
          },
          {
            "name": "E",
            "value": "2.71",
            "description": "The value of Euler's number.",
          },
        ]
    """

    result: list[Constant] = []

    for constant in node.findall("constant"):
        if constant.text is None or constant.text.strip() == '':
            continue
        if constant.attrib.get("enum", '') != '':
            continue

        result.append(parse_constant(constant))

    return result


def parse_enums(node: XMLNode) -> list[Enum]:
    """
    Parses a node with a list of constants into a list of enums.

    This function ignores the constants that don't have an enum attribute,
    which would make them just constants without an enum.

    For getting the solely constants, the parse_constants function should be used.

    Constants node structure::

        <constants>
          <constant name="ADDITION" value="0" enum="Operation">
            The addition operation.
          </constant>
          <constant name="SUBTRACTION" value="1" enum="Operation">
            The subtraction operation.
          </constant>
        </constants>

    Return structure::

        result = [
          {
            "name": "Operation",
            "values": [
              {
                "name": "ADDITION",
                "value": "0",
                "description": "The addition operation.",
              },
              {
                "name": "SUBTRACTION",
                "value": "1",
                "description": "The subtraction operation.",
              },
            ],
            "description": "",
          }
        ]
    """

    result: list[Enum] = []

    enums: dict[str, list[XMLNode]] = {}

    for constant in node.findall("constant"):
        enum_name = constant.attrib.get("enum", '')

        if enum_name == '':
            continue
        if constant.text is None or constant.text.strip() == '':
            continue

        if enums.get(enum_name) is None:
            enums[enum_name] = []

        enums[enum_name].append(constant)

    for enum in enums:
        values = enums[enum]

        result.append(parse_enum(enum, values))

    return result


def parse_theme_items(node: XMLNode) -> list[ThemeItem]:
    """
    Parses a node with a list of theme items into a list of dicts.

    Theme items node structure::

        <theme_items>
          <theme_item name="font_color" data_type="color" type="Color" default="black">
            The default font color.
          </theme_item>
          <theme_item name="font_size" data_type="int" type="int" default="14">
            The default font size.
          </theme_item>
        </theme_items>

    Return structure::

        result = [
          {
            "name": "font_color",
            "data_type": "color",
            "type": "Color",
            "default": "black",
            "description": "The default font color.",
          },
          {
            "name": "font_size",
            "data_type": "int",
            "type": "int",
            "default": "14",
            "description": "The default font size.",
          },
        ]
    """

    result: list[ThemeItem] = []

    for theme_item in node:
        if theme_item.text is None or theme_item.text.strip() == '':
            continue

        result.append(parse_theme_item(theme_item))

    return result


def parse_class(root: XMLNode, docs: list[XMLDoc]) -> Class:
    """
    Parses an XML node representing a Godot class into a convenient dict
    with separated information about the class members.

    The structure of the XML expected is the one generated by Godot's doctool
    and the generated dict has its structure defined in the Class type.
    """

    result: Class = {
        "name": '',
        "inheritage": [],
        "brief_description": '',
        "description": '',
        "properties": [],
        "methods": [],
        "signals": [],
        "constants": [],
        "enums": [],
        "theme_items": [],
    }

    result["name"] = root.attrib.get("name", '')
    result["inheritage"] = parse_inheritage(root, docs)
    result["brief_description"] = root \
        .find("brief_description").text.strip()  # type: ignore
    result["description"] = root \
        .find("description").text.strip()  # type: ignore

    for node in root:
        match node.tag:
            case "members": result["properties"] = parse_properties(node)
            case "methods": result["methods"] = parse_methods(node)
            case "signals": result["signals"] = parse_signals(node)
            case "constants":
                result["constants"] = parse_constants(node)
                result["enums"] = parse_enums(node)
            case "theme_items": result["theme_items"] = parse_theme_items(node)
            case _: pass

    return result


def create(
        docs: list[XMLDoc],
        options: dict[str, str] | None = None
) -> DocContext:
    """
    Creates a DocContext with information about all classes present in the
    docs list passed, as well as with data about the options desired to keep
    in context inside the options parameter.
    """

    if options is None:
        options = {}

    result: DocContext = {
        "options": options,
        "classes": [],
    }

    for doc in docs:
        root = doc.getroot()

        result["classes"].append(parse_class(root, docs))

    return result


def translate(ctx: DocContext, interpreter: Interpreter, translator: SyntaxTranslator):
    classes = ctx["classes"]
    for class_doc in classes:
        for member in class_doc:
            match(member):
                case "brief_description":
                    class_doc[member] = interpreter.interpret(
                        class_doc[member]).translate(translator)
                case "description":
                    class_doc[member] = interpreter.interpret(
                        class_doc[member]).translate(translator)
                case "constants":
                    constants = class_doc[member]
                    for constant in constants:
                        constant["description"] = interpreter.interpret(
                            constant["description"]).translate(translator)
                case "enums":
                    enums = class_doc[member]
                    for enum in enums:
                        enum["description"] = interpreter.interpret(
                            enum["description"]).translate(translator)
                        constants = enum["values"]
                        for constant in constants:
                            constant["description"] = interpreter.interpret(
                                constant["description"]).translate(translator)
                case "methods":
                    methods = class_doc[member]
                    for method in methods:
                        method["description"] = interpreter.interpret(
                            method["description"]).translate(translator)
                case "properties":
                    properties = class_doc[member]
                    for property in properties:
                        property["description"] = interpreter.interpret(
                            property["description"]).translate(translator)
                case "signals":
                    signals = class_doc[member]
                    for signal in signals:
                        signal["description"] = interpreter.interpret(
                            signal["description"]).translate(translator)
                case "theme_items":
                    theme_items = class_doc[member]
                    for theme_item in theme_items:
                        theme_item["description"] = interpreter.interpret(
                            theme_item["description"]).translate(translator)
                case _: pass

    return ctx
