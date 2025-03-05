#!/usr/bin/env python3

# Author: Akin Antony Wilson
# Contact: akinola.antony.wilson@gmail.com
# Institution: University of Nottingham, UK 
# Version: 1.0.0
# Date: 01-03-2025

"""
Compiling templating during github actions 
"""




import jinja2
import argparse
import json
import os
import errno 
from pathlib import Path
import subprocess
MAGENTA = "\033[35m"
BOLD = "\033[1m"
RESET = "\033[0m"


class Compiler:
    '''
    Compiles a seldon model release template, and saves it to ./models/<model_name>.yaml
    '''
    def __init__(self, model_name):
        self.model_name = model_name
        self.__call__()

    def __call__(self):
        template_file = Path(__file__).parent / "templates" / 'model_release.yaml.j2'
        output_dir = Path(__file__).parent / "models"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{self.model_name}.yaml"
        if output_file.exists():
            print(f"Release: {self.model_name} already exists. Using Retraction and deleting existing release {self.model_name}.yaml")
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