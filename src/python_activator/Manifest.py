import importlib
import json
import secrets
from pyld import jsonld
import logging
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse
import requests

import yaml

from .loader import (
    ManifestItem,
    generate_manifest_from_loaded_list,
    load_package,
    open_resource,
    set_object_directory,
)

import tempfile

object_directory = ""
Routing_Dictionary = {}
has_input_manifest = True

logger = logging.getLogger("Manifest")
# Create a log handler that sends messages to stderr
stderr_handler = logging.StreamHandler(sys.stderr)

# Configure logging to use the stderr handler
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
    handlers=[stderr_handler],
)

# create package path in os temp folder to be used to install packages
temp_dir = tempfile.gettempdir()
folder_name = "org-kgrid-python-activator"
temp_package_path = os.path.join(temp_dir, folder_name)
os.makedirs(temp_package_path, exist_ok=True)


class Manifest:
    def __init__(self):
        global object_directory
        object_directory = set_object_directory()

    def load_from_manifest(self):
        logging.info("Loading from manifest")

        ko_list = []
        manifest_path = os.environ.get("ORG_KGRID_PYTHON_ACTIVATOR_MANIFEST_PATH")
        if not manifest_path:
            logging.info("ORG_KGRID_PYTHON_ACTIVATOR_MANIFEST_PATH is not defined.")
            global has_input_manifest
            has_input_manifest = False
            return

        parsed_url = urlparse(manifest_path)
        if (
            not parsed_url.scheme
        ):  # If a scheme is not present, it's likely not a URL make it absolute path if not
            manifest_path = os.path.abspath(manifest_path)
            os.environ["ORG_KGRID_PYTHON_ACTIVATOR_MANIFEST_PATH"] = manifest_path

        resource = open_resource(manifest_path, "")
        input_manifest = json.loads(resource.read())  # load manifest

        # for each item in the manifest
        for manifest_item in input_manifest:
            ko = ManifestItem(
                manifest_item["@id"], manifest_item["url"], "uninitialized", None
            )
            try:
                load_package(object_directory, manifest_item["url"])
            except TypeError as e:
                ko.error = "Zip file not found: " + repr(e)
            except Exception as e:
                ko.error = "Error unzipping: " + repr(e)
            else:
                ko.status = "loaded"
            ko_list.append(ko)

            logging.info(ko.short_representation())
        generate_manifest_from_loaded_list(object_directory, ko_list)
        return ko_list

    def install_loaded_objects(self):
        if has_input_manifest:
            logging.info("Installing loaded objects")
        elif os.path.exists(Path(object_directory).joinpath("local_manifest.json")):
            logging.info("Installing objects from local manifest")
        else:
            logging.info("Local manifest does not exist")
            return {}, {}

        Knowledge_Objects = {}
        global Routing_Dictionary
        Routing_Dictionary = {}
        resource = open_resource(
            Path(object_directory).joinpath("local_manifest.json"), ""
        )
        local_manifest = json.loads(resource.read())  # load manifest
        for manifest_item in local_manifest:
            ko = Knowledge_Object(
                manifest_item["@id"],
                manifest_item["local_url"],
                manifest_item["status"],
                manifest_item["error"],
            )
            if manifest_item["status"] == "loaded":
                ko.install()
            Knowledge_Objects[manifest_item["@id"]] = ko
            logging.info(ko.short_representation())

        return Knowledge_Objects, Routing_Dictionary

    def uninstall_objects(self):
        logging.info("Uninstalling objects")
        resource = open_resource(
            Path(object_directory).joinpath("local_manifest.json"), ""
        )
        local_manifest = json.loads(resource.read())  # load manifest
        for manifest_item in local_manifest:
            try:
                subprocess.run(
                    ["pip", "uninstall", manifest_item["local_url"]], check=True
                )
                logging.info({"@id": manifest_item["@id"], "status": "uninstalled"})
            except Exception as e:
                logging.info(
                    {
                        "@id": manifest_item["@id"],
                        "status": "error uninstalling ",
                        "error": repr(e),
                    }
                )


class Knowledge_Object:
    metadata = None
    python_service = ""
    url = ""
    endpoints = None

    def __init__(self, id, local_url, status, error):
        try:
            with open(
                Path(object_directory).joinpath(local_url, "metadata.json"), "r"
            ) as file:
                self.metadata = json.load(file)

        except:
            self.metadata = {}
            pass
        self.metadata["@id"] = id
        self.metadata["status"] = status
        if error:
            self.metadata["error"] = error
        self.metadata["local_url"] = local_url

    def install(self):
        deployment_file = Path(object_directory).joinpath(
            self.metadata["local_url"],
            self.metadata.get("hasDeploymentSpecification", "deployment.yaml"),
        )
        self.python_service = Path(object_directory).joinpath(
            self.metadata["local_url"]
        )
        engine = ""
        # code to support kgrid object model version 2
        if (
            self.metadata.get("koio:kgrid", "") != ""
            and self.metadata["koio:kgrid"] == "2"
        ):
            deployment_file = ""  # reinitialize for kgrid 2 objects
            services = self.metadata["koio:hasService"]
            for service in services:
                if service["@type"] == "API" and service.get("implementedBy", "") != "":
                    implementations = service["implementedBy"]
                    for implementation in implementations:
                        service_type=implementation.get("@type", [])
                        if ("https://kgrid.org/specs/activationSpec.html#object" in service_type and "python" in service_type
                        ):
                            # load context
                            context = {"@context":self.metadata["@context"]}
                            if ".jsonld" in self.metadata["@context"]:
                                response = requests.get(self.metadata["@context"])
                                if response.status_code == 200:
                                    context = response.json()

                            # add @base to context
                            context["@context"]["@base"] = str(
                                Path(object_directory).joinpath(
                                    self.metadata["local_url"], " "
                                )
                            )

                            # expand implementation
                            implementation = jsonld.expand(
                                implementation,
                                {
                                    "expandContext": context,
                                    "base": str(
                                        Path(object_directory).joinpath(
                                            self.metadata["local_url"], " "
                                        )
                                    ),
                                },
                            )

                            # use resolved implementation id
                            deployment_file = Path(implementation[0]["@id"]).joinpath(
                                "deployment.yaml"
                            )
                            self.python_service = implementation[0]["@id"]
                            engine = "koio:org.kgrid.python-activator"
                            break

        try:
            if (
                deployment_file == ""
            ):  # if has no value means it is a kgrid 2 object with no python service
                return
            with open(deployment_file, "r") as file:
                self.endpoints = [
                    {"@id": self.metadata["@id"] + key, **obj}
                    for key, obj in yaml.safe_load(file).items()
                ]

            if self.metadata.get("koio:kgrid", "") == "":
                engine = (
                    "koio:" + self.endpoints[0]["post"]["engine"]["name"]
                )  # in case of version 1 use first endpoint engine

            # path to a folder in temp directory to install the new package
            module_path = os.path.join(
                temp_package_path, secrets.token_hex(8), self.metadata["@id"]
            )

            if engine == "koio:org.kgrid.python-activator":
                subprocess.run(
                    [
                        "pip",
                        "install",
                        "--force-reinstall",
                        "--upgrade",
                        "--target",
                        module_path,
                        self.python_service,
                    ],
                    check=True,
                )
                self.metadata["status"] = "installed"

        except Exception as e:
            self.metadata["error"] = "not installed " + repr(e)
            return

        all_endpoints_activated = True
        try:
            for endpoint in self.endpoints:
                try:
                    if (
                        endpoint["post"]["engine"]["name"]
                        != "org.kgrid.python-activator"
                    ):
                        return
                    package = endpoint["post"]["engine"]["package"]
                    module = endpoint["post"]["engine"]["module"]
                    function = endpoint["post"]["engine"]["function"]

                    # add module_path to sys.path temporarily
                    sys.path.insert(0, module_path)

                    # remove packages with the same name and their submodules from sys.modules before installing the new one
                    submodule_names = [
                        submodule_name
                        for submodule_name in sys.modules
                        if submodule_name.startswith(package)
                    ]
                    for submodule_name in submodule_names:
                        sys.modules.pop(submodule_name, None)

                    # Dynamically import the package
                    package_module = importlib.import_module(package + "." + module)

                    # Get the specific function from the module
                    endpoint["function"] = getattr(package_module, function)
                    endpoint["function"].description = str(endpoint["function"])
                    Routing_Dictionary[endpoint["@id"]] = endpoint

                    # remove module_path from sys.path
                    sys.path.remove(module_path)
                except Exception as e:
                    self.metadata["error"] = "error activating endpoint: " + repr(e)
                    all_endpoints_activated = False
            if all_endpoints_activated:
                self.metadata["status"] = "activated"
        except Exception as e:
            self.metadata["error"] = "error activating endpoint: " + repr(e)

    def short_representation(self):
        representation = {
            "@id": self.metadata["@id"] if self.metadata else "",
            "local_url": self.metadata["local_url"],
            "status": self.metadata["status"],
        }

        try:
            representation["error"] = self.metadata["error"]
        except Exception as e:
            pass

        return representation


class Route:
    def __init__(self, id, route):
        self.id = id
        self.route = route
