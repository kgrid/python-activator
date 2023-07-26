import os
from fastapi import HTTPException
from python_activator.loader import set_object_directory, load_package,open_resource
from python_activator.installer import install_package
import json
from pathlib import Path
import yaml
import json

object_directory=""

class KnowledgeObject:
    def __init__(self, name, manifestitem, status, function=None, id="", url="", entry="", function_name="", engine=""):
        self.id = id
        self.name = name
        self.status = status
        self.function = function
        self.url = url
        self.entry = entry
        self.manifestitem=manifestitem
        self.function_name=function_name
        self.engine=engine

    def load(self):
        try:
            load_package(object_directory,self.manifestitem)
        except TypeError as e:
            self.status= "Zip file not found: " + repr(e)
        except Exception as e:
           self.status=  "Error unziping: " + repr(e)    
        else: 
            self.status="Ready for install"       
            
    def configure(self):
        # get metadata and deployment files
            
        #########delete me: temporarily ignoring execute package
        if self.name == "python-executive-v1.0" or self.status!="Ready for install":
            return        
        modulepath = os.path.join(Path(object_directory).joinpath(self.name), "")

        with open(Path(modulepath).joinpath("deployment.yaml"), "r") as file:
            deployment_data = yaml.safe_load(file)
        with open(Path(modulepath).joinpath("metadata.json"), "r") as file:
            metadata = json.load(file)
        first_key = next(iter(deployment_data))
        second_key = next(iter(deployment_data[first_key]))     
        
        self.id=metadata["@id"]
        self.engine = deployment_data[first_key][second_key]["engine"]    
        
        if self.engine!="python":
            return
        
        self.entry = deployment_data[first_key][second_key]["entry"]
        self.function_name=deployment_data[first_key][second_key]["function"]        
            
    def install(self):
         # do not install non python packages
        if self.engine != "python":
            self.status="Knowledge object is not activated. It is not a python object."
            return
        
        if self.status!="Ready for install":
            return
                
        try:            
            self.function=install_package(object_directory,self.name, self.entry,self.function_name)
        except Exception as e:
            self.status=  "Error installing: " + repr(e)    
        else:
            self.status=  "Activated"   
            
                    
    async def execute(self, body):
        try:
            return self.function(body)
        except TypeError as e:
            raise HTTPException(
                status_code=422, 
                detail={"status": self.status, "cause": e.__cause__}
                )
            
class Manifest:
    Knowledge_Objects={}

        
    def __init__(self):   
        global object_directory
        object_directory = set_object_directory()
        self.Knowledge_Objects = self.load_manifest()
    
    def get_objects(self):
        return self.Knowledge_Objects.values()
        
    def load_manifest(self) -> dict:
        manifest_path = os.environ.get("MANIFEST_PATH")
        scanned_directories = [f.name for f in os.scandir(object_directory) if f.is_dir()]
        output_manifest = {}

        # 0. if no manifest provided consider list of existing knowledge object folders as manifest
        if not manifest_path:
            for item in scanned_directories:
                output_manifest[str.replace(item, ".zip", "")] = KnowledgeObject(
                    str.replace(item, ".zip", ""),item, "Ready for install",object_directory
                )
                
            return output_manifest

        resource=open_resource(manifest_path,"")
        input_manifest=json.loads(resource.read())["manifest"] #load manifest 

        # for each item in the manifest
        for manifest_item in input_manifest:

            ko_name = os.path.splitext(os.path.basename(manifest_item))[0]
            output_manifest[ko_name] = KnowledgeObject(ko_name, manifest_item,"",object_directory)

        return output_manifest    
        
    
        
         
        
        
        
        
        
