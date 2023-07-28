import os
import subprocess
from fastapi import HTTPException
from python_activator.loader import set_object_directory, load_package,open_resource
from python_activator.installer import install_package
import json
from pathlib import Path
import yaml
import json
import importlib

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


class ManifestItem:
    def __init__(self, id:str, directory:str, status:str):
        self.id = id
        self.directory = directory    
        self.status =   status 
            
class Manifest:
    Knowledge_Objects={}
    ko_list=[]
        
    def __init__(self):   
        global object_directory
        object_directory = set_object_directory()
        #self.Knowledge_Objects = self.load_manifest()
    
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
    
    @staticmethod 
    def generate_manifest_from_directory(directory: str):
        manifest=[]
        scanned_directories = [f.name for f in os.scandir(directory) if f.is_dir()]
        for sub_dir in scanned_directories:
            try:
                with open(Path(directory).joinpath(sub_dir,"metadata.json"), "r") as file:
                    metadata = json.load(file)                    
            except:
                continue
            
            metadata["local_url"]= sub_dir
            manifest.append(metadata)    
        #create a manifest
        print(manifest)
        with open(Path(directory).joinpath('local_manifest.json'), 'w') as json_file:
            json.dump(manifest, json_file,indent=2)
   
    def light_load_from_manifest(self)->list[ManifestItem]:
        manifest_path = os.environ.get("MANIFEST_PATH")
        resource=open_resource(manifest_path,"")
        input_manifest=json.loads(resource.read()) #load manifest 

        # for each item in the manifest
        for manifest_item in input_manifest:
            ko=ManifestItem(manifest_item["@id"],manifest_item["url"],"")
            try:
                load_package(object_directory,manifest_item["url"])
            except TypeError as e:
                ko.status= "Zip file not found: " + repr(e)
            except Exception as e:
                ko.status=  "Error unziping: " + repr(e)    
            else: 
                ko.status="Ready for install"    
            self.ko_list.append(ko)
        self.generate_manifest_from_directory(object_directory)    
        return self.ko_list   
    
    def install_loaded_objects(self):       
        
        resource=open_resource(Path(object_directory).joinpath("local_manifest.json"),"")
        local_manifest=json.loads(resource.read()) #load manifest 
        for manifest_item in local_manifest:
            ko=LightKnowledgeObject(manifest_item["local_url"])
            ko.install()
            self.Knowledge_Objects[manifest_item["@id"]]=ko
        return self.Knowledge_Objects
    
    def uninstall_objects(self):       
        
        resource=open_resource(Path(object_directory).joinpath("local_manifest.json"),"")
        local_manifest=json.loads(resource.read()) #load manifest 
        for manifest_item in local_manifest:
            
            subprocess.run(["pip", "uninstall", manifest_item["local_url"]], check=True)



    def set_object_directory(self,dir):
        global object_directory
        object_directory=dir
        os.environ["COLLECTION_PATH"]=dir
        
class LightKnowledgeObject:
    deployment_data=None
    metadata=None
    entry=""
    function_name=""
    local_url=""
    status=""
    url=""
    
    def __init__(self, local_url):
        self.local_url=local_url
        object_directory = set_object_directory()    
        with open(Path(object_directory).joinpath(local_url,"deployment.yaml"), "r") as file:
            self.deployment_data = yaml.safe_load(file)
        with open(Path(object_directory).joinpath(local_url,"metadata.json"), "r") as file:
            self.metadata = json.load(file) 
        
    def install(self):
        first_key = next(iter(self.deployment_data))
        second_key = next(iter(self.deployment_data[first_key]))     
              
        if self.deployment_data[first_key][second_key]["engine"] !="python":
            return
        
        
        self.entry = str.replace(self.deployment_data[first_key][second_key]["entry"],"src/","").replace(".py","")
        self.function_name=self.deployment_data[first_key][second_key]["function"]    
        
        try:
           subprocess.run(["pip", "install", Path(object_directory).joinpath(self.local_url)], check=True)
           self.status="installed"
        except Exception as e:
              self.status="installed" + repr(e)  
              
    async def execute(self, body):
        try:                         
            package_name = self.local_url+"."+self.entry
            function_name = self.function_name

            # Dynamically import the package
            package_module = importlib.import_module(package_name)

            # Get the specific function from the module
            function_to_call = getattr(package_module, function_name)

            # Call the function with any required arguments
            return function_to_call(body)  # Replace arg1, arg2 with actual function arguments
        except Exception as e:
            raise HTTPException(
                status_code=422, 
                detail={"status": repr(e)   }
                )   
        
