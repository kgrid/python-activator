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

logger = logging.getLogger("Manifest")
# Create a log handler that sends messages to stderr
stderr_handler = logging.StreamHandler(sys.stderr)

# Configure logging to use the stderr handler
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(name)s - %(funcName)s - %(message)s', handlers=[stderr_handler])


class Manifest:    
    def __init__(self):
        global object_directory
        object_directory = set_object_directory()


    def load_from_manifest(self) :
        logging.info("Loading from manifest")

        ko_list = []
        manifest_path = os.environ.get("MANIFEST_PATH")
        if not manifest_path:
            return
        
        parsed_url = urlparse(manifest_path)
        if not parsed_url.scheme:  # If a scheme is not present, it's likely not a URL make it absolute path if not
            manifest_path=os.path.abspath(manifest_path)
    
        resource = open_resource(manifest_path, "")
        input_manifest = json.loads(resource.read())  # load manifest

        # for each item in the manifest
        for manifest_item in input_manifest:
            ko = ManifestItem(manifest_item["@id"],manifest_item["url"], "")
            try:
                load_package(object_directory, manifest_item["url"])
            except TypeError as e:
                ko.status = "Zip file not found: " + repr(e)
            except Exception as e:
                ko.status = "Error unziping: " + repr(e)
            else:
                ko.status = "Ready for install"
            ko_list.append(ko)
            
            logging.info("ko "+ko.id + " - status "+ko.status)
        generate_manifest_from_loaded_list(object_directory,ko_list)
        return ko_list

    def install_loaded_objects(self):
        logging.info("Installing loaded objects")
        Knowledge_Objects={}
        Routing_Dictionary={}
        resource = open_resource(
            Path(object_directory).joinpath("local_manifest.json"), ""
        )
        local_manifest = json.loads(resource.read())  # load manifest
        for manifest_item in local_manifest:
            ko = Knowledge_Object(manifest_item["local_url"],manifest_item["status"])
            if manifest_item["status"]=="Ready for install":
                routes=ko.install()
                if routes:
                    for route in routes:
                        Routing_Dictionary[manifest_item["@id"]+route]=Route(manifest_item["@id"],route)
            Knowledge_Objects[manifest_item["@id"]] = ko
            logging.info("ko "+manifest_item["@id"] + " - status "+ko.status)

        return Knowledge_Objects,Routing_Dictionary

    def uninstall_objects(self):
        logging.info("Uninstalling objects")
        resource = open_resource(
            Path(object_directory).joinpath("local_manifest.json"), ""
        )
        local_manifest = json.loads(resource.read())  # load manifest
        for manifest_item in local_manifest:
            try:
                subprocess.run(["pip", "uninstall", manifest_item["local_url"]], check=True)
                logging.info("ko "+manifest_item["@id"] + " - status uninstalled")
            except Exception as e:
                logging.info("ko "+manifest_item["@id"] + " - status error uninstalling "+ repr(e))

class Knowledge_Object:
    deployment_data = None
    metadata = None
    function = {}
    local_url = ""
    status = ""
    url = ""

    def __init__(self, local_url,status):
        self.status = status
        
        try:
            with open(
                Path(object_directory).joinpath(local_url, "deployment.yaml"), "r"
            ) as file:
                self.deployment_data = yaml.safe_load(file)
            with open(
                Path(object_directory).joinpath(local_url, "metadata.json"), "r"
            ) as file:
                self.metadata = json.load(file)
        except:
            pass        
        self.local_url = local_url
        self.function = {}
        

    def install(self):
        
        
        try:
            routes = self.deployment_data["paths"].keys()
            subprocess.run(
                ["pip", "install", Path(object_directory).joinpath(self.local_url)],
                check=True,
            )

            for route in routes:
                if (self.deployment_data["paths"][route]["post"]["engine"]["name"]!= "org.kgrid.python-activator"):
                    return
                package = self.deployment_data["paths"][route]["post"]["engine"]["package"]
                module = self.deployment_data["paths"][route]["post"]["engine"]["module"]
                function = self.deployment_data["paths"][route]["post"]["engine"]["function"]

                # Dynamically import the package
                package_module = importlib.import_module(package + "." + module)

                # Get the specific function from the module
                self.function[route] = getattr(package_module, function)

            self.status = "installed"
            return routes
        except Exception as e:
            self.status = "not installed" + repr(e)

        
    async def execute(self, body, route):
        if route=="" and len(self.function)==1:
            return self.function[list(self.function.keys())[0]](body)
        else:
            return self.function[route](body)
        
class Route:
    def __init__(self,id,route):
        self.id=id
        self.route=route