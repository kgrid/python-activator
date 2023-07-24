import urllib.request
from urllib.parse import urlparse
import zipfile
import pathlib
import json
import os
from io import BytesIO
from pathlib import Path
from fastapi import HTTPException
from urllib import parse

class knowledge_object:
    def __init__(self, name, status, function=None, id="", url="", entry=""):
        self.id = id
        self.name = name
        self.status = status
        self.function = function
        self.url = url
        self.entry = entry

    async def execute(self, body):
        try:
            return self.function(body)
        except TypeError as e:
            raise HTTPException(
                status_code=422, 
                detail={"status": self.status, "cause": e.__cause__}
                )


def load_packages() -> dict:
    if os.environ.get("COLLECTION_PATH"):
        object_directory = os.path.join(Path(os.environ["COLLECTION_PATH"]), "")
    else:
        object_directory = os.path.join(Path(os.getcwd()).joinpath("pyshelf"), "")

    manifest_path = os.environ.get("MANIFEST_PATH")
    scanned_directories = [f.name for f in os.scandir(object_directory) if f.is_dir()]
    output_manifest = {}

    # 0. if no manifest provided consider list of existing knowledge object folders as manifest
    if not manifest_path:
        for item in scanned_directories:
            output_manifest[str.replace(item, ".zip", "")] = knowledge_object(
                str.replace(item, ".zip", ""), "Ready for install"
            )
            
            #create a manifest
            with open(Path(object_directory).joinpath('manifest_generated.json'), 'w') as json_file:
                json.dump({"manifest": [obj.name for obj in output_manifest.values()]}, json_file)

        return output_manifest, object_directory

    manifest_uri,resource=open_resource(manifest_path,"")
    input_manifest=json.loads(resource.read())["manifest"] #load manifest 

    # for each item in the manifest
    for i, manifest_item in enumerate(input_manifest):

        ko_name = os.path.splitext(os.path.basename(manifest_item))[0]

        output_manifest[ko_name] = knowledge_object(ko_name, "")

        # 1. if knowledge object already in the collection directory continue to the next ko in list
        if ko_name in scanned_directories:
            output_manifest[ko_name].status = "Ready for install"
            continue

        # 2. extract the knowledge object from the zip file in the uri (local or remote) in object directory
        try:
            ko_uri,resource=open_resource(manifest_path,manifest_item)
            with resource:
                 with zipfile.ZipFile(BytesIO(resource.read())) as zfile:
                     zfile.extractall(object_directory)
                     
        except TypeError as e:
            output_manifest[ko_name].status = "Zip file not found: " + repr(e)
            continue             
        except Exception as e:
            output_manifest[ko_name].status = "Error unziping: " + repr(e)
            continue

        output_manifest[ko_name].status = "Ready for install"

    return output_manifest, object_directory


def open_resource(base,relative):
    if os.path.isabs(base):  # if a local path create the URI
        base = pathlib.Path(base).as_uri()  # adds file:// if local path
        
    resolved=parse.urljoin(base, relative)
    try:
        resource=urllib.request.urlopen(resolved)
    except:
        resource=None    
        
    return resolved, resource
    