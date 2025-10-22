import json
from pathlib import Path

from aas_http_client import sdk_tools
from basyx.aas import model


def create_submodel_from_file(file_path: str) -> model.Submodel:
    """Creates a Submodel from a given file path.

    :param file_path: Path to the file containing the submodel data.
    :return: The created Submodel object.
    """
    file = Path(file_path)
    if not file.exists():
        raise FileNotFoundError(f"Submodel template file not found: {file}")

    template_data = {}

    # Load the template JSON file
    with open(file, "r", encoding="utf-8") as f:
        template_data = json.load(f)

    # Load the template JSON into a Submodel object
    return sdk_tools.convert_to_object(template_data)
