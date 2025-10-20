import json
import sys

from shapely import wkt
import dateutil.parser as date_parser
from shapely.geometry import shape

from arlas.cli.readers import get_data_generator
from arlas.cli.utils import is_float

MAX_KEYWORD_LENGTH = 100


def __build_tree__(tree: dict, o: any):
    """
    Recursively build a tree structure from a JSON object.
    The tree mirrors the JSON structure, with leaf nodes containing arrays of values in the "__items__" key.

    Args:
        tree (dict): The tree being built.
        o (any): The JSON object (dict, list, or primitive value) to process.

    Raises:
        Exception: If an unexpected state is encountered.
    """
    if o is not None:
        if type(o) is dict:
            o: dict = o
            for (k, v) in o.items():
                tree[k] = tree.get(k, {})
                __build_tree__(tree[k], v)
        else:
            if type(o) is list:
                o: list = o
                for c in o:
                    if type(c) is dict or type(c) is list:
                        ...  # We can not manage arrays of objects :-(
                    else:
                        # An array of values should become a simple type field. 
                        # For instance, list[int] becomes int since ES manages int as int or list[int]
                        __build_tree__(tree, c)
            else:
                values: list = tree.get("__items__", [])
                tree["__items__"] = values
                values.append(o)
    else:
        ...


def __type_tree__(path: str, tree: dict, forced_types: dict[str, str]):
    """
    Recursively infer types for nodes in the tree of values.

    Uses __type_node__ to determine the type of each node based on its values.

    Args:
        path (str): The current path in the tree (e.g., "user.name").
        tree (dict): The tree built by __build_tree__.
        forced_types (dict[str, str]): Predefined types for specific fields.

    Raises:
        Exception: If an unexpected state is encountered.
    """
    if type(tree) is dict:
        for (k, v) in tree.items():
            if path:
                subpath = ".".join([path, k])
            else:
                subpath = k
            if subpath in forced_types:
                tree[k]["__type__"] = forced_types.get(subpath)
            else:
                if k == "__type__":
                    ...
                else:
                    if type(v) is dict:
                        if v.get("__items__"):
                            # it is a leaf, we need to get the type
                            tree[k]["__type__"] = __type_node__(v.get("__items__"), k)
                        else:
                            # it is either an intermediate node or a complex type such as geojson
                            t = __type_node__(v, k)
                            tree[k]["__type__"] = t
                            if t == "object":
                                # it is an intermediate node, we dive in the node
                                __type_tree__(subpath, v, forced_types)
                    else:
                        raise Exception("Unexpected state")
    else:
        raise Exception("Unexpected state")


# Type a node. Here is the "guessing"
def __type_node__(items: list | dict, name: str = "") -> str:
    """
    Infer the type of a node based on its values.

    Args:
        items (list | dict): List of values or GeoJSON dictionary.
        name (str, optional): The field name, used for type hints (e.g., dates, geohashes).

    Returns:
        str: The inferred type ("geo_point", "date", "text", etc.).

    Raises:
        Exception: If an unexpected state is encountered.
    """
    if isinstance(items, dict):
        # Handle geojson dict and nested fields (set as 'object' here)
        if "type" in items and "coordinates" in items and "__items__" in items.get("type", []):
            # looks like geojson ...
            types = items.get("type", {}).get("__items__", [])
            if all([t.lower() in ["point", "multipoint"] for t in types]):
                return "geo_point"
            if all([t.lower() in ["point", "multipoint", "linestring", "multistring", "polygon", "multipolygon",
                                  "geometrycollection"] for t in types]):
                return "geo_shape"
            else:
                return "object"
        else:
            return "object"
    if isinstance(items, list):
        if len(items) == 0:
            # Empty values
            pass
        # Handle list of values
        types_list = [__type_value__(field_value=item, field_name=name) for item in items]
        types_set = set(types_list)
        types_set.discard("UNDEFINED")
        if len(types_set) == 0:
            # Only undefined types
            pass
        elif types_set == {"boolean"}:
            return "boolean"
        elif types_set == {"double"} or types_set == {"double", "long"}:
            return "double"
        elif types_set == {"long"}:
            if len(name) > 0 and (name.find("timestamp") >= 0 or name.find("_date") >= 0 or name.find("date_") >= 0 or
                                  name.find("start_") >= 0 or name.find("_start") >= 0 or name.find("_end") >= 0 or
                                  name.find("end_") >= 0):
                # all between year 1950 and 2100, in second or millisecond
                if all((x > 631152000 and x < 4102444800) for x in items):
                    return "date-epoch_second"
                if all((x > 631152000000 and x < 4102444800000) for x in items):
                    return "date-epoch_millis"
                else:
                    return "long"
            else:
                return "long"
        elif types_set == {"date"}:
            return "date"
        elif types_set == {"geo_point"}:
            return "geo_point"
        elif types_set == {"geo_shape"} or types_set == {"geo_shape", "geo_point"}:
            return "geo_shape"
        elif types_set == {"keyword"}:
            return "keyword"
        elif types_set == {"text"} or types_set == {"text", "keyword"}:
            return "text"

        # No valid type has been detected
        print(f"Error: No valid type has been found for field '{name}' with values: {items} (types: {types_set})",
              file=sys.stderr)
        return "UNDEFINED"
    else:
        raise Exception(f"Unexpected state when inferring type of '{name}': {items}")


def __type_value__(field_value, field_name: str) -> str:
    """
    Infer the type of a single value.

    Args:
        field_value (any): The value to analyze.
        field_name (str, optional): The field name, used for type hints (e.g., dates, geohashes).

    Returns:
        str: The inferred type ("geo_point", "date", "keyword", etc.).
    """
    if field_value is None:
        return "UNDEFINED"
    elif isinstance(field_value, bool):
        return "boolean"
    elif isinstance(field_value, int):
        return "long"
    elif isinstance(field_value, float):
        return "double"
    elif isinstance(field_value, str):
        # Geo objects ...
        if field_value.startswith("POINT "):
            try:
                wkt.loads(field_value)
                return "geo_point"
            except Exception:
                ...
        if field_value.startswith("LINESTRING ") or field_value.startswith("POLYGON ") or field_value.startswith(
                "MULTIPOINT ") or field_value.startswith("MULTILINESTRING ") or field_value.startswith("MULTIPOLYGON "):
            # Looks like WKT
            try:
                wkt.loads(field_value)
                return "geo_shape"
            except Exception:
                ...
        if len(field_name) > 0 and field_name.find("geohash") >= 0:
            return "geo_point"
        if ("coordinates" in field_value) and ("type" in field_value):
            # Looks like geojson as str
            try:
                geo_dict = json.loads(field_value)
                # Validate the geometry
                shapely_geom = shape(geo_dict)
                if shapely_geom.geom_type in ["Point", "MultiPoint"]:
                    return "geo_point"
                elif shapely_geom.geom_type in ["LineString", "Polygon", "MultiLinestring","MultiPolygon",
                                                "GeometryCollection"]:
                    return "geo_shape"
            except Exception:
                ...
        lat_lon: list[str] = field_value.split(",")
        if len(lat_lon) == 2 and is_float(lat_lon[0].strip()) and is_float(lat_lon[1].strip()):
            return "geo_point"
        # Date objects ...
        if len(field_name) > 0 and (field_name.find("timestamp") >= 0 or field_name.find("date") >= 0 or
                                    field_name.find("start") >= 0 or field_name.find("end") >= 0):
            try:
                date_parser.parse(field_value)
                return "date"
            except Exception:
                ...
        if len(field_value) < MAX_KEYWORD_LENGTH:
            return "keyword"
        else:
            return "text"

    return "UNDEFINED"


# from the typed tree, generate the mapping.
def __generate_mapping__(tree: dict, mapping: dict, no_fulltext: list[str], no_index: list[str],
                         field_path: str = None):
    """
    Generate an Elasticsearch mapping from the typed tree.

    Args:
        tree (dict): The typed tree.
        mapping (dict): The Elasticsearch mapping being built.
        no_fulltext (list[str]): Fields to exclude from full-text search.
        no_index (list[str]): Fields to exclude from indexing.
        field_path (str, optional): The current field path.

    Raises:
        Exception: If an unexpected state is encountered.
    """
    if type(tree) is dict:
        for (field_name, v) in tree.items():
            if field_name not in ["__type__", "__values__"]:
                field_type: str = v.get("__type__")
                if field_type == "object":
                    mapping[field_name] = {"properties": {}}
                    if field_path is None:
                        new_field_path = field_name
                    else:
                        new_field_path = ".".join([field_path, field_name])
                    __generate_mapping__(tree=v, mapping=mapping[field_name]["properties"], no_fulltext=no_fulltext,
                                         no_index=no_index, field_path=new_field_path)
                else:
                    if field_type.startswith("date-"):
                        # Dates can have format patterns containing '-'
                        mapping[field_name] = {"type": "date", "format": field_type.split("-", 1)[1]}
                    else:
                        mapping[field_name] = {"type": field_type}
                        if field_type in ["keyword", "text"]:
                            if field_name not in no_fulltext:
                                mapping[field_name]["copy_to"] = ["internal.fulltext", "internal.autocomplete"]
                    # Avoid indexing field if field in --no-index
                    if field_name in no_index:
                        mapping[field_name]["index"] = "false"
                    if field_path is not None:
                        full_name = ".".join([field_path, field_name])
                    else:
                        full_name = field_name
                    print(f"-->{full_name}: {mapping[field_name]['type']}")
    else:
        raise Exception("Unexpected state")


def make_mapping(file: str, nb_lines: int = 2, types: dict[str, str] = {}, no_fulltext: list[str] = [],
                 no_index: list[str] = [], file_type: str = None):
    """
    Generate an Elasticsearch mapping from a data file.
    Reads the first `nb_lines` lines of the file, infers field types, and generates an Elasticsearch mapping.

    Args:
        file (str): Path to the data file.
        nb_lines (int, optional): Number of lines to analyze. Defaults to 2.
        types (dict[str, str], optional): Predefined types for specific fields.
        no_fulltext (list[str], optional): Fields to exclude from full-text search.
        no_index (list[str], optional): Fields to exclude from indexing.
        file_type (str, optional): Type of the file (e.g., "json", "ndjson").

    Returns:
        dict: The Elasticsearch mapping.
    """
    # Read file
    data_generator = get_data_generator(file_path=file, file_type=file_type, max_lines=nb_lines)

    # Parse the file first lines values
    tree = {}
    for hit in data_generator:
        __build_tree__(tree, hit)

    # Identify fields types
    __type_tree__("", tree, types)

    # Generate the mapping
    mapping = {}
    __generate_mapping__(tree, mapping, no_fulltext, no_index)
    mapping["internal"] = {
        "properties": {
            "autocomplete": {
                "type": "keyword"
            },
            "fulltext": {
                "type": "text",
                "fielddata": True
            }
        }
    }
    return {
        "mappings": {
            "properties": mapping
        }
    }


def read_override_mapping_fields(field_mapping: list[str]) -> dict[str, str]:
    """Parse a list of field:mapping overrides into a dictionary.

    Args:
        field_mapping: List of strings in the format "field:type" or "field:date-format".
                      Example: ["timestamp:date-epoch_second", "location:geo_point"]

    Returns:
        dict[str, str]: Dictionary mapping field paths to their types.

    Raises:
        SystemExit: If any field_mapping entry is invalid.
    """
    types = {}

    for mapping_entry in field_mapping:
        # Handle date formats (which contain additional colons)
        if ":" not in mapping_entry:
            print(
                f'Error: invalid field_mapping "{mapping_entry}". '
                f'The format is "field:type" like "fragment.location:geo_point"',
                file=sys.stderr,
            )
            exit(1)

        # Split on first colon only to handle date formats like "date:yyyy-MM-dd"
        field, field_type = mapping_entry.split(":", 1)
        types[field] = field_type

    return types
