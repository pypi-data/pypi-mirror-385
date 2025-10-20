from pathlib import Path
import xml.etree.ElementTree as ET

type XMLNode = ET.Element[str]

type XMLDoc = ET.ElementTree[XMLNode]


def parse_file(path: str | Path) -> XMLDoc:
    """
    Parses an XML file from a given path and returns an ElementTree object.

    Args:
      path: Path to the XML file.

    Returns:
      Parsed ElementTree containing the XML data.

    Raises:
        FileNotFoundError: If the file at the given path does not exist.
        xml.etree.ElementTree.ParseError: If the file is not a valid XML document.
    """

    return ET.parse(path)


def parse_folder(path: str | Path) -> list[XMLDoc]:
    """
    Parses all XML files from a given path and returns a list with ElementTree objects.

    Args:
      path: Path to the folder containing XML files.

    Returns:
      List with the parsed ElementTrees containing the XML data.

    Raises:
        NotADirectoryError: If the path doesn't point to a directory.
    """

    path = Path(path)

    if not path.is_dir():
        raise NotADirectoryError(f"{path} is not a directory")

    return [parse_file(subpath) for subpath in path.glob("*.xml")]


def parse(path: str | Path) -> list[XMLDoc]:
    """
    Parses one or more XML files from a given path.

    If the path points to a file, parses that file.
    If the path points to a directory, parses all XML files in the directory.
    Returns a list of parsed ElementTree objects.

    Args:
      path: Path to an XML file or a directory containing XML files.

    Returns:
      A list of ElementTree objects parsed from the XML files.

    Raises:
        FileNotFoundError: If the file at the given path does not exist.
        xml.etree.ElementTree.ParseError: If the file is not a valid XML document.
    """

    path = Path(path)

    return [parse_file(path)] if path.is_file() else parse_folder(path)
