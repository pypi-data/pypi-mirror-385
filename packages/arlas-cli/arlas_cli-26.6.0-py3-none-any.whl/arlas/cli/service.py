from enum import Enum
import json
import os
import sys
import urllib.parse
from urllib.parse import urlencode
from datetime import datetime

from alive_progress import alive_bar
import requests
from prettytable import PrettyTable

from arlas.cli.readers import get_data_generator
from arlas.cli.settings import ARLAS, Configuration, Resource, AuthorizationService
from arlas.cli.utils import is_valid_uuid

requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)


def default_handler(obj):
    if obj is None:
        return {}
    raise TypeError(f'Object of type {obj.__class__.__name__} is not JSON serializable')


class RequestException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class Services(Enum):
    arlas_server = "server"
    persistence_server = "persistence"
    iam = "iam"


class Service:
    curl: bool = False

    @staticmethod
    def test_arlas_server(arlas: str):
        try:
            Service.__arlas__(arlas, "explore/_list", exit_on_failure=False)
            return "ok"
        except Exception as e:
            return "not ok ({} ...)".format(str(e)[:20])

    @staticmethod
    def test_arlas_iam(arlas: str):
        try:
            Service.__arlas__(arlas, "organisations", service=Services.iam, exit_on_failure=False)
            return "ok"
        except Exception as e:
            return "not ok ({} ...)".format(str(e)[:20])

    @staticmethod
    def test_arlas_persistence(arlas: str):
        try:
            url = "/".join(["persist", "resources", "config.json"]) + "?size=10000&page=1&order=desc&pretty=false"
            Service.__arlas__(arlas, url, service=Services.persistence_server, exit_on_failure=False)
            return "ok"
        except Exception as e:
            return "not ok ({} ...)".format(str(e)[:20])

    @staticmethod
    def test_es(arlas: str):
        try:
            Service.__es__(arlas, "/".join(["*"]), exit_on_failure=False)
            return "ok"
        except Exception as e:
            return "not ok ({} ...)".format(str(e)[:20])

    @staticmethod
    def create_user(arlas: str, email: str):
        return Service.__arlas__(arlas, "users", post=json.dumps({"email": email}), service=Services.iam)

    @staticmethod
    def describe_user(arlas: str, id: str):
        return Service.__arlas__(arlas, "/".join(["users", id]), service=Services.iam)

    @staticmethod
    def update_user(arlas: str, id: str, oldPassword: str = None, newPassword: str = None, locale: str = None, timezone: str = None, firstName: str = None, lastName: str = None):
        data = {"oldPassword": oldPassword}
        if newPassword:
            data["newPassword"] = newPassword
        if locale:
            data["locale"] = locale
        if timezone:
            data["timezone"] = timezone
        if firstName:
            data["firstName"] = firstName
        if lastName:
            data["lastName"] = lastName
        return Service.__arlas__(arlas, "/".join(["users", id]), put=json.dumps(data), service=Services.iam)

    @staticmethod
    def delete_user(arlas: str, id: str):
        return Service.__arlas__(arlas, "/".join(["users", id]), delete=True, service=Services.iam)

    @staticmethod
    def activate(arlas: str, id: str):
        return Service.__arlas__(arlas, "/".join(["users", id, "activate"]), post="{}", service=Services.iam)
    
    @staticmethod
    def deactivate(arlas: str, id: str):
        return Service.__arlas__(arlas, "/".join(["users", id, "deactivate"]), post="{}", service=Services.iam)

    @staticmethod
    def reset_password(arlas: str, email: str):
        return Service.__arlas__(arlas, "/".join(["users", "resetpassword"]), post=email, service=Services.iam)

    @staticmethod
    def list_organisations(arlas: str) -> list[list[str]]:
        data = Service.__arlas__(arlas, "organisations", service=Services.iam)
        table = [["id", "name", "Am I owner?"]]
        for org in data:
            table.append([
                org.get("id"),
                org.get("name") + " (" + org.get("displayName") + ")",
                org.get("isOwner"),
            ])
        return table

    @staticmethod
    def create_organisation(arlas: str, org: str):
        return Service.__arlas__(arlas, "/".join(["organisations", org]), post="{}", service=Services.iam)

    @staticmethod
    def create_organisation_from_user_domain(arlas: str):
        return Service.__arlas__(arlas, "organisations", post="{}", service=Services.iam)

    @staticmethod
    def delete_organisation(arlas: str, oid: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid]), delete=True, service=Services.iam)

    @staticmethod
    def list_organisation_collections(arlas: str, oid: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "collections"]), service=Services.iam)

    @staticmethod
    def list_organisation_users(arlas: str, oid: str):
        users: list = Service.__arlas__(arlas, "/".join(["organisations", oid, "users"]), service=Services.iam)
        return list(map(lambda user: [user.get("member").get("id"),
                                      user.get("member").get("email"),
                                      user.get("isOwner"),
                                      "\n".join(list(map(lambda role: role.get("fullName"), user.get("member").get("roles"))))],
                        users))

    @staticmethod
    def get_user_from_organisation(arlas: str, oid: str, user: str):
        users: list = Service.__arlas__(arlas, "/".join(["organisations", oid, "users"]), service=Services.iam)
        users: list = list(filter(lambda u: u.get("member").get("email") == user, users))
        if len(users) > 0:
            return list(map(lambda user: [user.get("member").get("id"),
                                          user.get("member").get("email"),
                                          user.get("isOwner"),
                                          "\n".join(list(map(lambda role: role.get("fullName"), user.get("member").get("roles"))))], users))[0]
        return None

    @staticmethod
    def list_organisation_groups(arlas: str, oid: str):
        groups: list = Service.__arlas__(arlas, "/".join(["organisations", oid, "groups"]), service=Services.iam)
        return list(map(lambda user: [user.get("id"),
                                      user.get("fullName"),
                                      user.get("description"),
                                      user.get("isTechnical"),
                                      "group"
                                      ],
                        groups))

    @staticmethod
    def add_user_in_organisation(arlas: str, oid: str, email: str, groups: list[str]):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "users"]), post=json.dumps({"email": email, "rids": groups}), service=Services.iam)

    @staticmethod
    def delete_user_in_organisation(arlas: str, oid: str, user_id: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "users", user_id]), delete=True, service=Services.iam)

    @staticmethod
    def add_group_in_organisation(arlas: str, oid: str, group_name: str, group_description: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "groups"]), post=json.dumps({"name": group_name, "description": group_description}), service=Services.iam)

    @staticmethod
    def delete_group_in_organisation(arlas: str, oid: str, group_id: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "groups", group_id]), delete=True, service=Services.iam)

    @staticmethod
    def add_permission_in_organisation(arlas: str, oid: str, permission_value: str, permission_description: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "permissions"]), post=json.dumps({"value": permission_value, "description": permission_description}), service=Services.iam)

    @staticmethod
    def delete_permission_in_organisation(arlas: str, oid: str, permission_id: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "permissions", permission_id]), delete=True, service=Services.iam)

    @staticmethod
    def add_permission_to_group_in_organisation(arlas: str, oid: str, role_id: str, permission_id: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "roles", role_id, "permissions", permission_id]), post="{}", service=Services.iam)

    @staticmethod
    def delete_permission_from_group_in_organisation(arlas: str, oid: str, role_id: str, permission_id: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "roles", role_id, "permissions", permission_id]), delete=True, service=Services.iam)

    @staticmethod
    def add_user_to_organisation_group(arlas: str, oid: str, uid: str, role_id: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "users", uid, "roles", role_id]), post="{}", service=Services.iam)

    @staticmethod
    def remove_user_from_organisation_group(arlas: str, oid: str, uid: str, role_id: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "users", uid, "roles", role_id]), delete=True, service=Services.iam)

    @staticmethod
    def add_role_in_organisation(arlas: str, oid: str, role_name: str, role_description: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "roles"]), post=json.dumps({"name": role_name, "description": role_description}), service=Services.iam)

    @staticmethod
    def delete_role_in_organisation(arlas: str, oid: str, role_id: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "roles", role_id]), delete=True, service=Services.iam)

    @staticmethod
    def list_organisation_roles(arlas: str, oid: str):
        roles: list = Service.__arlas__(arlas, "/".join(["organisations", oid, "roles"]), service=Services.iam)
        return list(map(lambda user: [user.get("id"),
                                      user.get("name"),
                                      user.get("description"),
                                      user.get("isTechnical"),
                                      "role"
                                      ],
                        roles))

    @staticmethod
    def list_organisation_permissions(arlas: str, oid: str):
        permissions: list = Service.__arlas__(arlas, "/".join(["organisations", oid, "permissions"]), service=Services.iam)
        return list(map(lambda perm: [perm.get("id"),
                                      perm.get("description"),
                                      perm.get("value"),
                                      "\n".join(list(map(lambda role: role.get("fullName"), perm.get("roles"))))
                                      ],
                        permissions))

    @staticmethod
    def list_collections(arlas: str) -> list[list[str]]:
        data = Service.__arlas__(arlas, "explore/_list")
        table = [["name", "index"]]
        for collection in data:
            table.append([
                collection.get("collection_name"),
                collection.get("params", {}).get("index_name"),
            ])
        return table

    @staticmethod
    def list_indices(arlas: str, keep_only: str = None) -> list[list[str]]:
        data = json.loads(Service.__es__(arlas, "_cat/indices?format=json"))
        table = [["name", "status", "count", "size"]]
        for index in data:
            if keep_only is None or keep_only == index.get("index"):
                table.append([
                    index.get("index"),
                    index.get("status"),
                    index.get("docs.count"),
                    index.get("store.size")
                ])
        return table

    @staticmethod
    def set_collection_visibility(arlas: str, collection: str, public: bool):
        description = Service.__arlas__(arlas, "/".join(["explore", collection, "_describe"]))
        doc = {
            "shared": description.get("params", {}).get("organisations", {}).get("shared", []),
            "public": public
        }
        return Service.__arlas__(arlas, "/".join(["collections", collection, "organisations"]), patch=json.dumps(doc)).get("params", {}).get("organisations", {}).get("public")

    @staticmethod
    def set_collection_display_name(arlas: str, collection: str, name: str):
        doc = name
        return Service.__arlas__(arlas, "/".join(["collections", collection, "display_names", "collection"]), patch=json.dumps(doc)).get("params", {}).get("display_names", {}).get("collection")

    @staticmethod
    def set_collection_field_display_name(arlas: str, collection: str, field_name: str, field_display_name: str):
        collection_description = Service.__arlas__(arlas, "/".join(["collections", collection]))
        aliasses: dict[str, str] = collection_description.get("display_names", {}).get("fields", {})
        if field_display_name:
            aliasses[field_name] = field_display_name
        else:
            if aliasses.get(field_display_name):
                # Remove the alias
                aliasses.pop(field_display_name)
        table = [["field path", "display name"]]
        for path, name in Service.__arlas__(arlas, "/".join(["collections", collection, "display_names", "fields"]), patch=json.dumps(aliasses)).get("params", {}).get("display_names", {}).get("fields", {}).items():
            table.append([path, name])
        return table

    @staticmethod
    def share_with(arlas: str, collection: str, organisation: str):
        description = Service.__arlas__(arlas, "/".join(["explore", collection, "_describe"]))
        orgs = description.get("params", {}).get("organisations", {}).get("shared", [])
        if organisation not in orgs:
            orgs.append(organisation)
        doc = {
            "organisations": {
                "shared": orgs,
                "public": description.get("params", {}).get("organisations", {}).get("public", False)
            }
        }
        return Service.__arlas__(arlas, "/".join(["collections", collection, "organisations"]), patch=json.dumps(doc)).get("params", {}).get("organisations", {}).get("shared")

    @staticmethod
    def unshare_with(arlas: str, collection: str, organisation: str):
        description = Service.__arlas__(arlas, "/".join(["explore", collection, "_describe"]))
        orgs: list = description.get("params", {}).get("organisations", {}).get("shared", [])
        if organisation in orgs:
            orgs.remove(organisation)
        else:
            print("Warning: {} not shared with {}".format(collection, organisation))
        doc = {
            "organisations": {
                "shared": orgs,
                "public": description.get("params", {}).get("organisations", {}).get("public", False)
            }
        }
        return Service.__arlas__(arlas, "/".join(["collections", collection, "organisations"]), patch=json.dumps(doc)).get("params", {}).get("organisations", {}).get("shared")

    @staticmethod
    def describe_collection(arlas: str, collection: str) -> list[list[str]]:
        description = Service.__arlas__(arlas, "/".join(["explore", collection, "_describe"]))
        table = [["field name", "type"]]
        table.extend(Service.__get_fields__([], description.get("properties", {})))
        return table

    @staticmethod
    def metadata_collection(arlas: str, collection: str) -> list[list[str]]:
        d = Service.__arlas__(arlas, "/".join(["explore", collection, "_describe"]))
        table = [["metadata", "value"]]
        table.append(["index name", d.get("params", {}).get("index_name", {})])
        table.append(["id path", d.get("params", {}).get("id_path", "")])
        table.append(["geometry path", d.get("params", {}).get("geometry_path", "")])
        table.append(["centroid path", d.get("params", {}).get("centroid_path", "")])
        table.append(["timestamp path", d.get("params", {}).get("timestamp_path", "")])
        table.append(["display name", d.get("params", {}).get("display_names", {}).get("collection", "")])
        table.append(["owner", d.get("params", {}).get("organisations", {}).get("owner", "")])
        table.append(["is public", d.get("params", {}).get("organisations", {}).get("public", False)])
        table.append(["organisations", str(d.get("params", {}).get("organisations", {}).get("shared", []))])
        return table
    
    @staticmethod
    def describe_index(arlas: str, index: str) -> list[list[str]]:
        description = json.loads(Service.__es__(arlas, "/".join([index, "_mapping"])))
        table = [["field name", "type"]]
        table.extend(Service.__get_fields__([], description.get(index, {}).get("mappings", {}).get("properties", {})))
        return table
    
    @staticmethod
    def clone_index(arlas: str, index: str, name: str) -> list[list[str]]:
        Service.__es__(arlas, "/".join([index, "_block", "write"]), put="")
        Service.__es__(arlas, "/".join([index, "_clone", name]), put="")
        Service.__es__(arlas, "/".join([index, "_settings"]), put='{"index.blocks.write": false}')
        return Service.list_indices(arlas, keep_only=name)
    
    @staticmethod
    def migrate_index(arlas: str, index: str, target_arlas: str, target_name: str) -> list[list[str]]:
        source = Configuration.settings.arlas.get(arlas)
        migration = {
            "source": {
                "remote": {
                    "host": source.elastic.location,
                    "username": source.elastic.login,
                    "password": source.elastic.password,
                },
                "index": index,
                "query": {"match_all": {}},
            },
            "dest": {"index": target_name},
        }
        print("1/3: fetch mapping ...")
        mapping = Service.__es__(arlas, "/".join([index, "_mapping"]))
        mapping = json.dumps(json.loads(mapping).get(index))
        print("2/3: copy mapping ...")
        Service.__es__(target_arlas, "/".join([target_name]), put=mapping)
        print("3/3: copy data ...")
        print(Service.__es__(target_arlas, "/".join(["_reindex"]), post=json.dumps(migration)))
        return Service.list_indices(target_arlas, keep_only=target_name)
    
    @staticmethod
    def sample_collection(arlas: str, collection: str, pretty: bool, size: int) -> dict:
        sample = Service.__arlas__(arlas, "/".join(["explore", collection, "_search"]) + "?size={}".format(size))
        return sample

    @staticmethod
    def sample_index(arlas: str, collection: str, pretty: bool, size: int) -> dict:
        sample = json.loads(Service.__es__(arlas, "/".join([collection, "_search"]) + "?size={}".format(size)))
        return sample
    
    @staticmethod
    def create_collection(arlas: str, collection: str, model_resource: str, index: str, display_name: str, owner: str, orgs: list[str], is_public: bool, id_path: str, centroid_path: str, geometry_path: str, date_path: str):
        if model_resource:
            model = json.loads(Service.__fetch__(model_resource))
        else:
            model = {}
        if index:
            model["index_name"] = index
        if not owner:
            configuration: ARLAS = Configuration.settings.arlas.get(arlas, None)
            if configuration and configuration.authorization and configuration.authorization.token_url and configuration.authorization.token_url.headers and configuration.authorization.token_url.headers.get("arlas-org-filter"):
                owner = configuration.authorization.token_url.headers.get("arlas-org-filter")
        if owner:
            model["organisations"] = {
                "owner": owner,
                "shared": orgs,
                "public": is_public
            }
        if id_path:
            model["id_path"] = id_path
        if centroid_path:
            model["centroid_path"] = centroid_path
        if geometry_path:
            model["geometry_path"] = geometry_path
        if date_path:
            model["timestamp_path"] = date_path
        if display_name:
            display_names = model.get("display_names", {})
            display_names["collection"] = display_name
            model["display_names"] = display_names
        Service.__arlas__(arlas, "/".join(["collections", collection]), put=json.dumps(model))

    @staticmethod
    def create_index_from_resource(arlas: str, index: str, mapping_resource: str, number_of_shards: int):
        mapping = json.loads(Service.__fetch__(mapping_resource))
        if not mapping.get("mappings"):
            print("Error: mapping {} does not contain \"mappings\" at its root.".format(mapping_resource), file=sys.stderr)
            exit(1)
        Service.create_index(arlas, index, mapping, number_of_shards)

    @staticmethod
    def create_index(arlas: str, index: str, mapping: str, number_of_shards: int = 1):
        index_doc = {"mappings": mapping.get("mappings"), "settings": {"number_of_shards": number_of_shards}}
        Service.__es__(arlas, "/".join([index]), put=json.dumps(index_doc))

    @staticmethod
    def delete_collection(arlas: str, collection: str):
        Service.__arlas__(arlas, "/".join(["collections", collection]), delete=True)

    @staticmethod
    def delete_index(arlas: str, index: str):
        Service.__es__(arlas, "/".join([index]), delete=True)

    @staticmethod
    def count_collection(arlas: str, collection: str) -> list[list[str]]:
        collections = []
        if collection:
            collections.append(collection)
        else:
            for line in Service.list_collections(arlas)[1:]:
                collections.append(line[0])
        table = [["collection name", "count"]]
        for collection in collections:
            count = Service.__arlas__(arlas, "/".join(["explore", collection, "_count"]))
            table.append([collection, count.get("totalnb", "UNKNOWN")])
        return table

    @staticmethod
    def count_hits(file_path: str) -> int:
        line_number = 0
        with open(file_path, mode="r", encoding="utf-8") as f:
            for line in f:
                line_number = line_number + 1
        return line_number

    @staticmethod
    def persistence_add_file(arlas: str, file: Resource, zone: str, name: str, encode: bool = False, readers: list[str] = [], writers: list[str] = []):
        content = Service.__fetch__(file, bytes=True)
        url = "/".join(["persist", "resource", zone, name]) + "?" + "&".join(list(map(lambda r: "readers=" + urllib.parse.quote_plus(r), readers)) + list(map(lambda w: "writers=" + urllib.parse.quote_plus(w), writers)))
        return Service.__arlas__(arlas, url, post=content, service=Services.persistence_server).get("id")

    @staticmethod
    def persistence_delete(arlas: str, id: str):
        url = "/".join(["persist", "resource", "id", id])
        return Service.__arlas__(arlas, url, delete=True, service=Services.persistence_server)

    @staticmethod
    def persistence_get(arlas: str, id: str):
        url = "/".join(["persist", "resource", "id", id])
        return Service.__arlas__(arlas, url, service=Services.persistence_server)
    
    @staticmethod
    def persistence_zone(arlas: str, zone: str):
        url = "/".join(["persist", "resources", zone]) + "?size=10000&page=1&order=desc&pretty=false"
        table = [["id", "name", "zone", "last_update_date", "owner"]]
        entries = Service.__arlas__(arlas, url, service=Services.persistence_server).get("data", [])
        for entry in entries:
            table.append([entry["id"], entry["doc_key"], entry["doc_zone"], entry["last_update_date"], entry["doc_owner"]])
        return table

    @staticmethod
    def persistence_groups(arlas: str, zone: str):
        url = "/".join(["persist", "groups", zone])
        table = [["group"]]
        groups = Service.__arlas__(arlas, url, service=Services.persistence_server)
        for group in groups:
            table.append([group])
        return table

    @staticmethod
    def persistence_describe(arlas: str, id: str):
        url = "/".join(["persist", "resource", "id", id])
        r = Service.__arlas__(arlas, url, service=Services.persistence_server)
        table = [["metadata", "value"]]
        table.append(["ID", r.get("id")])
        table.append(["name", r.get("doc_key")])
        table.append(["zone", r.get("doc_zone")])
        table.append(["last_update_date", datetime.fromtimestamp(r.get("last_update_date") / 1000.0).isoformat()])
        table.append(["owner", r.get("doc_owner")])
        table.append(["organization", r.get("doc_organization")])
        table.append(["ispublic", r.get("ispublic")])
        table.append(["updatable", r.get("updatable")])
        table.append(["readers", ", ".join(r.get("doc_readers", []))])
        table.append(["writers", ", ".join(r.get("doc_writers", []))])
        return table

    @staticmethod
    def create_api_key(arlas: str, oid: str, name: str, ttlInDays: int, uid: str, gids: list[str]):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "users", uid, "apikeys"]), post=json.dumps({"name": name, "ttlInDays": ttlInDays, "roleIds": gids}), service=Services.iam)

    @staticmethod
    def delete_api_key(arlas: str, oid: str, uid: str, keyid: str):
        return Service.__arlas__(arlas, "/".join(["organisations", oid, "users", uid, "apikeys", keyid]), delete=True, service=Services.iam)

    @staticmethod
    def check_organisation(arlas: str):
        return Service.__arlas__(arlas, "/".join(["organisations", "check"]), service=Services.iam)

    @staticmethod
    def forbidden_organisations(arlas: str):
        return Service.__arlas__(arlas, "/".join(["organisations", "forbidden"]), service=Services.iam)

    @staticmethod
    def forbid_organisation(arlas: str, name: str):
        return Service.__arlas__(arlas, "/".join(["organisations", "forbidden"]), post=json.dumps({"name": name}), service=Services.iam)

    @staticmethod
    def authorize_organisation(arlas: str, name: str):
        return Service.__arlas__(arlas, "/".join(["organisations", "forbidden", name]), delete=True, service=Services.iam)

    @staticmethod
    def __index_bulk__(arlas: str, index: str, bulk: []):
        data = os.linesep.join([json.dumps(line) for line in bulk]) + os.linesep
        result = json.loads(Service.__es__(arlas, "/".join([index, "_bulk"]), post=data, exit_on_failure=False, headers={"Content-Type": "application/x-ndjson"}))
        if result["errors"] is True:
            print("ERROR: " + json.dumps(result))

    @staticmethod
    def index_hits(arlas: str, index: str, file_path: str, bulk_size: int = 5000, count: int = -1) -> dict[str, int]:
        line_number = 0
        line_in_bulk = 0
        bulk = []

        # Get index mapping
        field_mapping = dict(Service.describe_index(arlas=arlas, index=index))
        # Read data
        data_generator = get_data_generator(file_path=file_path, fields_mapping=field_mapping)

        with alive_bar(count) as bar:
            for line in data_generator:
                line_number = line_number + 1
                line_in_bulk = line_in_bulk + 1
                bulk.append({
                    "index": {
                        "_index": index
                    }
                })
                bulk.append(line)
                if line_in_bulk == bulk_size:
                    try:
                        Service.__index_bulk__(arlas, index, bulk)
                    except RequestException as e:
                        print(f"Error on bulk insert between line {line_number} and {line_number - bulk_size} "
                              f"with code {e.code}: {e.message}")
                    bulk = []
                    line_in_bulk = 0
                bar()
        if len(bulk) > 0:
            try:
                Service.__index_bulk__(arlas, index, bulk)
            except RequestException as e:
                print(f"Error on bulk insert between line {line_number} and {line_number - bulk_size} "
                      f"with code {e.code}: {e.message}")

    @staticmethod
    def __get_fields__(origin: list[str], properties: dict[str:dict]):
        fields = []
        for field, desc in properties.items():
            type = desc.get("type", "UNKNOWN")
            if type == "OBJECT" or type == "UNKNOWN":
                o = origin.copy()
                o.append(field)
                fields.extend(Service.__get_fields__(o, desc.get("properties", {})))
            else:
                o = origin.copy()
                o.append(field)
                fields.append([".".join(o), type])
        return fields
    
    @staticmethod
    def __arlas__(arlas: str, suffix, post=None, put=None, patch=None, delete=None, service=Services.arlas_server, exit_on_failure: bool = False):
        configuration: ARLAS = Configuration.settings.arlas.get(arlas, None)
        if configuration is None:
            print("Error: arlas configuration {} not found among [{}] for {}.".format(arlas, ", ".join(Configuration.settings.arlas.keys()), service.name), file=sys.stderr)
            exit(1)
        if service == Services.arlas_server:
            __headers__ = configuration.server.headers.copy()
            endpoint: Resource = configuration.server
        elif service == Services.persistence_server:
            __headers__ = configuration.persistence.headers.copy()
            endpoint: Resource = configuration.persistence
        elif service == Services.iam:
            __headers__ = configuration.authorization.token_url.headers.copy()
            endpoint: Resource = configuration.authorization.token_url.model_copy()
            endpoint.location = endpoint.location.rsplit('/', 1)[0]

        if Configuration.settings.arlas.get(arlas).authorization is not None:
            __headers__["Authorization"] = "Bearer " + Service.__get_token__(arlas)
        url = "/".join([endpoint.location, suffix])
        try:
            method = "GET"
            data = None
            if post:
                data = post
                method = "POST"
            if patch:
                data = patch
                method = "PATCH"
            if put:
                data = put
                method = "PUT"
            if delete:
                method = "DELETE"
            r: requests.Response = Service.__request__(url, method, data, __headers__)
            if r.status_code >= 200 and r.status_code < 300:
                return r.json()
            else:
                print("Error: request {} failed with status {}: {}".format(method, str(r.status_code), str(r.reason)), file=sys.stderr)
                print("   url: {}".format(url), file=sys.stderr)
                print(r.content)
                exit(1)
        except Exception as e:
            if exit_on_failure:
                print("Error: request {} failed on {}".format(method, e), file=sys.stderr)
                print("   url: {}".format(url), file=sys.stderr)
                exit(1)
            else:
                raise e

    @staticmethod
    def __es__(arlas: str, suffix, post=None, put=None, delete=None, exit_on_failure: bool = True, headers: dict[str, str] = {}):
        endpoint = Configuration.settings.arlas.get(arlas)
        if endpoint is None:
            print("Error: arlas configuration {} not found among [{}].".format(arlas, ", ".join(Configuration.settings.arlas.keys())), file=sys.stderr)
            exit(1)
        if endpoint.elastic is None:
            print("Error: arlas configuration {} misses an elasticsearch configuration.".format(arlas), file=sys.stderr)
            exit(1)
        url = "/".join([endpoint.elastic.location, suffix])
        __headers = endpoint.elastic.headers
        __headers.update(headers)
        auth = (endpoint.elastic.login, endpoint.elastic.password) if endpoint.elastic.login else None
        method = "GET"
        data = None
        if post is not None:
            data = post
            method = "POST"
        if put is not None:
            data = put
            method = "PUT"
        if delete is not None:
            method = "DELETE"
        r: requests.Response = Service.__request__(url, method, data, __headers, auth)
        if r.status_code >= 200 and r.status_code < 300:
            return r.content
        elif exit_on_failure:
            print("Error: request {} failed with status {}: {}".format(method, str(r.status_code), str(r.reason)), file=sys.stderr)
            print("   url: {}".format(url), file=sys.stderr)
            print(r.content)
            if r.status_code == 403:
                print("IMPORTANT: This error occurs because you are not allowed to trigger this arlas_cli action. If you are using ARLAS Cloud, please check that you have not used up your quota. You can contact support@gisaia.com for help.", file=sys.stderr)
            exit(1)
        else:
            raise RequestException(r.status_code, r.content)

    @staticmethod
    def __request__(url: str, method: str, data: any = None, headers: dict[str, str] = {}, auth: tuple[str, str | None] = None) -> requests.Response:
        if Service.curl:
            print('curl -k -X {} "{}" {}'.format(method.upper(), url, " ".join(list(map(lambda h: '--header "' + h + ":" + headers.get(h) + '"', headers)))), end="")
            if (method.upper() in ["POST", "PUT"]):
                print(" -d {}".format(data))
        if method.upper() == "POST":
            r = requests.post(url, data=data, headers=headers, auth=auth, verify=False)
        elif method.upper() == "PATCH":
            r = requests.patch(url, data=data, headers=headers, auth=auth, verify=False)
        elif method == "PUT":
            r = requests.put(url, data=data, headers=headers, auth=auth, verify=False)
        elif method == "DELETE":
            r = requests.delete(url, headers=headers, auth=auth, verify=False)
        else:
            r = requests.get(url, headers=headers, auth=auth, verify=False)
        return r

    @staticmethod
    def __fetch__(resource: Resource, bytes: bool = False):
        if os.path.exists(resource.location):
            content = None
            mode = "r"
            if bytes:
                mode = "rb"
            with open(resource.location, mode) as f:
                content = f.read()
            return content
        r: requests.Response = requests.get(resource.location, headers=resource.headers, verify=False)
        if r.status_code >= 200 and r.status_code < 300:
            return r.content
        else:
            print("Error: request failed with status {}: {}".format(str(r.status_code), str(r.reason)), file=sys.stderr)
            print("   url: {}".format(resource.location), file=sys.stderr)
            exit(1)

    @staticmethod
    def __get_token__(arlas: str) -> str:
        auth: AuthorizationService = Configuration.settings.arlas[arlas].authorization
        if auth.arlas_iam:
            data = {
                "email": auth.token_url.login,
                "password": auth.token_url.password
            }
        else:
            data = {}
            if auth.client_id:
                data["client_id"] = auth.client_id
            if auth.client_secret:
                data["client_secret"] = auth.client_secret
            if auth.token_url.login:
                data["username"] = auth.token_url.login
            if auth.token_url.password:
                data["password"] = auth.token_url.password
            if auth.grant_type:
                data["grant_type"] = auth.grant_type
        if auth.arlas_iam:
            data = json.dumps(data, default=default_handler)
        else:
            data = urlencode(data)
        if Service.curl:
            print('curl -k -X {} "{}" {}'.format("POST", auth.token_url.location, " ".join(list(map(lambda h: '--header "' + h + ":" + auth.token_url.headers.get(h) + '"', auth.token_url.headers)))), end="")
            print(" -d '{}'".format(data))
        r = requests.post(
            headers=auth.token_url.headers,
            data=data,
            url=auth.token_url.location,
            verify=False)
        if r.status_code >= 200 and r.status_code < 300:
            if r.json().get("accessToken"):
                return r.json()["accessToken"]
            elif r.json().get("access_token"):
                return r.json()["access_token"]
            else:
                print("Error: Failed to find access token in response {}".format(r.content), file=sys.stderr)
                print("   url: {}".format(auth.token_url.location), file=sys.stderr)
                exit(1)
        else:
            print("Error: request to get token failed with status {}: {}".format(str(r.status_code), r.content), file=sys.stderr)
            print("   url: {}".format(auth.token_url.location), file=sys.stderr)
            exit(1)

    @staticmethod
    def get_organisation_uuid(org_id: str, arlas: str) -> str:
        """
        Retrieve the UUID of an organisation from its name or validate an existing UUID.

        This function first checks if the provided `org_id` is a valid UUID. If it is, the UUID is
        returned directly. If not, the function queries the ARLAS IAM service using the provided
        `arlas` endpoint to find an organisation matching the given name. If found, its UUID is
        returned. If no match is found, an error message is printed, the list of available
        organisations is displayed, and the program exits with an error code.

        Args:
            org_id (str):
                The organisation identifier. It can be either:
                - A valid UUID (e.g., "8684d6d0-a466-4622-89e3-beda9daf7843").
                - The name of the organisation (e.g., "my_org").
            arlas (str):
                Name of the ARLAS configuration to use.

        Returns:
            str:
                The UUID of the organisation if found or validated. Example:
                "8684d6d0-a466-4622-89e3-beda9daf7843".

        Raises:
            SystemExit:
                Exits the program with status code 1 if the organisation is not found.
                This occurs when:
                - `org_id` is not a valid organisation UUID.
                - `org_id` is not a valid organisation name
        """
        if is_valid_uuid(uuid=org_id):
            return org_id
        else:
            # Get organisation list
            orgs_info = Service.__arlas__(arlas, "organisations", service=Services.iam)
            for organisation in orgs_info:
                if organisation["name"] == org_id:
                    return organisation["id"]

        organisations = Service.list_organisations(arlas)
        tab = PrettyTable(organisations[0], sortby="name", align="l")
        tab.add_rows(organisations[1:])
        print(f"Organisation '{org_id}' not found among:")
        print(tab)
        exit(1)
