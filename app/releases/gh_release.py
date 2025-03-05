#!/usr/bin/env python3

# Author: Akin Antony Wilson
# Contact: akinola.antony.wilson@gmail.com
# Institution: University of Nottingham, UK 
# Version: 1.0.0
# Date: 01-03-2025

"""
This tool is a helper for managing the deployment of a model to a local cluster using the Seldon Core workflow
The templating engine jinja is used to compile a template corresponding to the release of a model, along with
a dashboard to Grafana for the released model and an exposed endpoint. The deployment manifest template 
is found in templates/model_release.yaml.j2. The script handles both the release or retraction of a model from 
the field. 

The compiled manifest are supposed to be pickup by ArgoCD during push to the main branch and ArgoCD is 
configured to look for a folder containing the path releases/models. Hence The script below ensures 
the deployed manifests are saved in this location. 

Currently, rather than applying the deployment to the cluster via the GitOps route, the k8s client is used 
below to update configMaps required to be alter belonging to Seldon, and used a subprocess call to kubectl 
to either deploy or delete deployments

The script currently only handles default model releases, templates for AB, shadow and canary deployments 
still need to be created. 
"""




import jinja2
import argparse
import json
import os
import errno 
# from kubernetes import client, config
# from kubernetes.client.rest import ApiException
from pathlib import Path
import subprocess
MAGENTA = "\033[35m"
BOLD = "\033[1m"
RESET = "\033[0m"


# class AbsPath:
#     '''
#         helper for finding model/release folder independent of where script is called form 
#         assuming only one folder containing releases/models exists in the filesystem 
#         TODO: Raise Error if more than one matching directory exists 
#     '''    
#     def __init__(self, start_node = Path("/"), node_link = "releases/models"):
#         self.start_node : Path = start_node
#         self.node_link = node_link
    
    
#     def search(self):
#         try:
#             for p in self.start_node.rglob(self.node_link):
#                 try:
#                     if p.is_dir():
#                         return p.resolve()  # Return first matching directory
#                 except PermissionError:
#                     continue  # Skip directories where permission is denied
#         except PermissionError:
#             pass  # Skip if root-level scanning fails
#         return None 
#     def __call__(self):
#         abs_path = self.search()
#         if abs_path:
#             return str(abs_path)
#         else:
#             err_msg = (
#             f"Absolute path {self.node_link} could not be found.\n\n"
#             f"Folder containing subpath `{BOLD}{MAGENTA}releases/models{RESET}` or `{BOLD}{MAGENTA}releases/templates{RESET}` "
#             f"is supposed to contain Seldon model deployment manifests and the templates which generate them. "
#             f"Subpath provided did not match required pattern."
#         )
#             raise FileNotFoundError(errno.ENOENT, err_msg, self.node_link)
    
#     def __str__(self):
#         return self.__call__()
            
        
class Compiler:
    '''
    Compiles a seldon model release template, and saves it to ./models/<model_name>.yaml
    '''
    def __init__(self, model_name):
        self.model_name = model_name
        self.__call__()

    def __call__(self):
        template_file = Path(__file__).parent / 'model_release.yaml.j2'
        output_dir = Path(__file__).parent / "models"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{self.model_name}.yaml"
        if output_file.exists():
            print(f"Release: {self.model_name} already exists. Deleting existing release {self.model_name}.yaml")
            output_file.unlink()
            return

        else: 
            with open(template_file, 'r') as file:
                template_content = file.read()
            env = jinja2.Environment()
            template = env.from_string(template_content)
            rendered_yaml = template.render(model_name=self.model_name)
            # Write the rendered output to a file named after the model name
            with open(output_file, 'w') as file:
                file.write(rendered_yaml)
            print(f"Generated release manifest file for model.\n\n'{self.model_name}': {output_file}")
            

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Model release template generation for default deployment.")
    parser.add_argument('--image-uri', required=True, help="The image URI (e.g., 'docker.io/akinolawilson/t5-small:fc5e18ab')")
    args = parser.parse_args()
    model_name = args.image_uri.split(":")[-1] # The name of the model to generate release manifests 
    # compile model release 
    Compiler(model_name)
    
    
    
if __name__ == "__main__":
    main()