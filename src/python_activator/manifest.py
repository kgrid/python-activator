import urllib.request
import zipfile
import pathlib
import json
import requests
import os
from pathlib import Path
class ko_object:
    def __init__(self, name, status):
        self.name = name
        self.status = status
        
    
        
def process_manifest(object_directory: str)->dict:
    manifest_path = os.environ.get("MANIFEST_PATH")
    scanned_directories=[f.name for f in os.scandir(object_directory) if f.is_dir()]
    output_manifest={}
    
    # 0. if no manifest provided consider list of existing knowledge object folders as manifest
    if not manifest_path:
        for item in scanned_directories:
            output_manifest[str.replace(item, ".zip", "")]=ko_object(str.replace(item, ".zip", ""),"Ready for install")
        return output_manifest

    input_manifest, scanned_files = init_process(manifest_path, object_directory)
    
    
    
    # for each item in the manifest
    for i, item in enumerate(input_manifest):  
        ko_path, ko_name, ko_filename = set_ko_info(manifest_path, item)

        output_manifest[ko_name]=ko_object(ko_name, "")

        # 1. if knowledge object already in the collection directory continue to the next ko in list
        if (
            ko_name in scanned_directories            
        ):
            output_manifest[ko_name].status="Ready for install"            
            continue

        # 2. if zip file does not exists in the folder download it from local path or http (uses uri)
        
        if not ko_filename in scanned_files:
            try:
                urllib.request.urlretrieve(
                    get_uri(ko_path), os.path.join(Path(object_directory),ko_filename)
                )
                output_manifest[ko_name].status="Package zip file downloaded"     
            except Exception as e:
                # if file did not exist in source give warning and continue to the next ko
                print("warning: could not find the knowledge object " + ko_name)
                output_manifest[ko_name].status="Package zip file not found"     
                continue
        else:
            output_manifest[ko_name].status="Package zip file found in the directory"     


        # 3. extract the knowledge object from the zip file in object directory
        try:
            with zipfile.ZipFile(os.path.join(Path(object_directory),ko_filename), "r") as zip_ref:
             zip_ref.extractall(object_directory)
        except Exception as e:
            output_manifest[ko_name].status="Error unziping: " + + repr(e) 

        output_manifest[ko_name].status="Ready for install"            

        
    # create a new manifest with full path
    return output_manifest


def get_uri(path: str):
    uri = path
    if os.path.exists(path):  # if a local path create the URI
        uri = pathlib.Path(path).as_uri()  # adds file:// if local path
    return uri


def get_json_content(path):
    if path.startswith("http://") or path.startswith("https://"):
        # Path is a URL
        response = requests.get(path)
        data = response.json()
    else:
        # Path is a local file
        with open(path, "r") as file:
            data = json.load(file)

    return data


def init_process(manifest_path, object_directory):
    input_manifest = get_json_content(manifest_path)["manifest"]
    scanned_files = [f.name for f in os.scandir(object_directory) if f.is_file()]
    return input_manifest, scanned_files


def set_ko_info(manifest_path, manifest_item):
    ko_path = manifest_item
    if not os.path.isdir(manifest_item):  # extract knowledge object path
        ko_path = os.path.dirname(manifest_path) + "/" + manifest_item
      
    ko_name = os.path.splitext(os.path.basename(manifest_item))[0]

    ko_filename = os.path.basename(ko_path)
    return ko_path, ko_name, ko_filename
