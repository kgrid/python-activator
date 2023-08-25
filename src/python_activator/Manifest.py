import importlib
import json
import logging
import os
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

import yaml

from python_activator.loader import (
    ManifestItem,
    generate_manifest_from_loaded_list,
    load_package,
    open_resource,
    set_object_directory,
)

object_directory = ""
Routing_Dictionary = {}

logger = logging.getLogger("Manifest")
# Create a log handler that sends messages to stderr
stderr_handler = logging.StreamHandler(sys.stderr)

# Configure logging to use the stderr handler
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s",
    handlers=[stderr_handler],
)


class Manifest:
    def __init__(self):
        global object_directory
        object_directory = set_object_directory()

    def load_from_manifest(self):
        logging.info("Loading from manifest")

        ko_list = []
        manifest_path = os.environ.get("MANIFEST_PATH")
        if not manifest_path:
            return

        parsed_url = urlparse(manifest_path)
        if (
            not parsed_url.scheme
        ):  # If a scheme is not present, it's likely not a URL make it absolute path if not
            manifest_path = os.path.abspath(manifest_path)
            os.environ["MANIFEST_PATH"] = manifest_path

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
        logging.info("Installing loaded objects")
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
                        "status": "error uninstalling ","error": repr(e),
                    }
                )


class Knowledge_Object:
    metadata = None

    url = ""

    def __init__(self, id, local_url, status, error):
        try:
            with open(
                Path(object_directory).joinpath(local_url, "metadata.json"), "r"
            ) as file:
                self.metadata = json.load(file)

            with open(
                Path(object_directory).joinpath(local_url, "deployment.yaml"), "r"
            ) as file:
                self.metadata["hasDeploymentSpecification"] = [
                    {"@id": id + key, **obj}
                    for key, obj in yaml.safe_load(file).items()
                ]

        except:
            self.metadata = {}
            pass
        self.metadata["@id"] = id
        self.metadata["status"] = status
        if error:
            self.metadata["error"] = error
        self.metadata["local_url"] = local_url

    def install(self):
        try:
            subprocess.run(
                [
                    "pip",
                    "install",
                    Path(object_directory).joinpath(self.metadata["local_url"]),
                ],
                check=True,
            )
            self.metadata["status"] = "installed"
        except Exception as e:
            self.metadata["error"] = "not installed " + repr(e)

        all_endpoints_activated = True
        for endpoint in self.metadata["hasDeploymentSpecification"]:
            try:
                if endpoint["post"]["engine"]["name"] != "org.kgrid.python-activator":
                    return
                package = endpoint["post"]["engine"]["package"]
                module = endpoint["post"]["engine"]["module"]
                function = endpoint["post"]["engine"]["function"]

                # Dynamically import the package
                package_module = importlib.import_module(package + "." + module)

                # Get the specific function from the module

                endpoint["function"] = getattr(package_module, function)
                endpoint["function"].description = str(endpoint["function"])
                Routing_Dictionary[endpoint["@id"]] = endpoint
            except Exception as e:
                self.metadata["error"] = "error activating endpoint: " + repr(e)
                all_endpoints_activated = False
        if all_endpoints_activated:
            self.metadata["status"] = "activated"

    def short_representation(self):
        representation= {
            "@id": self.metadata["@id"] if self.metadata else "",
            "local_url": self.metadata["local_url"],
            "status": self.metadata["status"],
        }
        
        try:
            representation["error"]=self.metadata["error"] 
        except Exception as e:
            pass
        
        return representation


class Route:
    def __init__(self, id, route):
        self.id = id
        self.route = route
