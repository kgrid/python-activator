import os
import subprocess
from fastapi import HTTPException
from python_activator.loader import set_object_directory, load_package, open_resource
import json
from pathlib import Path
import yaml
import json
import importlib

object_directory = ""


class ManifestItem:
    def __init__(self, id: str, directory: str, status: str):
        self.id = id
        self.directory = directory
        self.status = status


class Manifest:
    Knowledge_Objects = {}
    ko_list = []

    def __init__(self):
        global object_directory
        object_directory = set_object_directory()

    def get_objects(self):
        return self.Knowledge_Objects.values()

    @staticmethod
    def generate_manifest_from_directory(directory: str):
        manifest = []
        scanned_directories = [f.name for f in os.scandir(directory) if f.is_dir()]
        for sub_dir in scanned_directories:
            try:
                with open(
                    Path(directory).joinpath(sub_dir, "metadata.json"), "r"
                ) as file:
                    metadata = json.load(file)
            except:
                continue

            metadata["local_url"] = sub_dir
            manifest.append(metadata)
        # create a manifest
        print(manifest)
        with open(Path(directory).joinpath("local_manifest.json"), "w") as json_file:
            json.dump(manifest, json_file, indent=2)

    def load_from_manifest(self) -> list[ManifestItem]:
        manifest_path = os.environ.get("MANIFEST_PATH")
        resource = open_resource(manifest_path, "")
        input_manifest = json.loads(resource.read())  # load manifest

        # for each item in the manifest
        for manifest_item in input_manifest:
            ko = ManifestItem(manifest_item["@id"], manifest_item["url"], "")
            try:
                load_package(object_directory, manifest_item["url"])
            except TypeError as e:
                ko.status = "Zip file not found: " + repr(e)
            except Exception as e:
                ko.status = "Error unziping: " + repr(e)
            else:
                ko.status = "Ready for install"
            self.ko_list.append(ko)
        self.generate_manifest_from_directory(object_directory)
        return self.ko_list

    def install_loaded_objects(self):
        resource = open_resource(
            Path(object_directory).joinpath("local_manifest.json"), ""
        )
        local_manifest = json.loads(resource.read())  # load manifest
        for manifest_item in local_manifest:
            ko = Knowledge_Object(manifest_item["local_url"])
            ko.install()
            self.Knowledge_Objects[manifest_item["@id"]] = ko
        return self.Knowledge_Objects

    def uninstall_objects(self):
        resource = open_resource(
            Path(object_directory).joinpath("local_manifest.json"), ""
        )
        local_manifest = json.loads(resource.read())  # load manifest
        for manifest_item in local_manifest:
            subprocess.run(["pip", "uninstall", manifest_item["local_url"]], check=True)

    def set_object_directory(self, dir):
        global object_directory
        object_directory = dir
        os.environ["COLLECTION_PATH"] = dir


class Knowledge_Object:
    deployment_data = None
    metadata = None
    function = None
    local_url = ""
    status = ""
    url = ""

    def __init__(self, local_url):
        object_directory = set_object_directory()
        with open(
            Path(object_directory).joinpath(local_url, "deployment.yaml"), "r"
        ) as file:
            self.deployment_data = yaml.safe_load(file)
        with open(
            Path(object_directory).joinpath(local_url, "metadata.json"), "r"
        ) as file:
            self.metadata = json.load(file)
        self.local_url = local_url

    def install(self):
        routes = self.deployment_data["paths"].keys()
        try:
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
                self.function = getattr(package_module, function)

            self.status = "installed"
        except Exception as e:
            self.status = "not installed" + repr(e)

    async def execute(self, body):
        try:
            return self.function(body)
        except Exception as e:
            raise HTTPException(status_code=422, detail={"status": repr(e)})
