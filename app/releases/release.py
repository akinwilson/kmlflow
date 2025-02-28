#!/usr/bin/env python3
import jinja2
import argparse
import json
import os
import errno 
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from pathlib import Path
import subprocess

MAGENTA = "\033[35m"
BOLD = "\033[1m"
RESET = "\033[0m"


class AbsoluteFolderPath:
    '''
        helper for finding model/release folder independent of where script is called form 
        assuming only one folder containing releases/models exists in the filesystem 

        TODO: Raise Error if more than one matching directory exists 
    '''    
    def __init__(self, start_node = Path("/"), node_link = "releases/models"):
        self.start_node : Path = start_node
        self.node_link = node_link
    
    
    def search(self):
        try:
            for p in self.start_node.rglob(self.node_link):
                try:
                    if p.is_dir():
                        return p.resolve()  # Return first matching directory
                except PermissionError:
                    continue  # Skip directories where permission is denied
        except PermissionError:
            pass  # Skip if root-level scanning fails
        return None 

    def __call__(self):
        abs_path = self.search()
        if abs_path:
            return str(abs_path)
        else:
            err_msg = (
            f"Absolute path {self.node_link} could not be found.\n\n"
            f"Folder containing subpath `{BOLD}{MAGENTA}releases/models{RESET}` or `{BOLD}{MAGENTA}releases/templates{RESET}` "
            f"is supposed to contain Seldon model deployment manifests and the templates which generate them. "
            f"Subpath provided did not match required pattern."
        )
            raise FileNotFoundError(errno.ENOENT, err_msg, self.node_link)
    
    def __str__(self):
        return self.__call__()

            
        


class Compiler:
    '''
    Compiles a seldon model release template, and saves it to ./models/<model_name>.yaml
    '''
    def __init__(self, model_name, remove=False, add=True):
        self.model_name = model_name
        assert remove != add, "Cannot remove and add a model release manifest. If you wish to over write an existing release, set add=True"
        
        self.remove = remove 
        self.add = add 
        self.__call__()


    def __call__(self):
        template_file = Path(str(AbsoluteFolderPath(node_link="releases/templates")))  / 'model_release.yaml.j2'
        output_dir = Path(str(AbsoluteFolderPath(node_link="releases/models"))) 

        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"{self.model_name}.yaml"
        if self.remove:
            if output_file.exists():
                # let the inferenceServerManger first delete the object
                return
                # print(f"Removing model release file: {output_file}")
                # output_file.unlink()
                # return
        if self.add: 
            if output_file.exists():
                print(f"Release manifest for model {self.model_name} exists already, overwriting existing release.")
            
            with open(template_file, 'r') as file:
                template_content = file.read()
            env = jinja2.Environment()
            template = env.from_string(template_content)
            rendered_yaml = template.render(model_name=self.model_name)
            # Write the rendered output to a file named after the model name
            with open(output_file, 'w') as file:
                file.write(rendered_yaml)
            print(f"Generated YAML file for model release.\n\n'{self.model_name}': {output_file}")
            
class InferenceServerManager:
    """
    Handles updating the Seldon Core ConfigMap with new inference servers, either adding or removing servers.
    """
    def __init__(self, image_uri, add=False, remove=False):
        self.image_uri = image_uri
        self.img_name, self.tag = image_uri.split(':')
        self.server_name = f"{self.tag.upper()}_SERVER"
        self.add = add
        self.remove = remove

        self.model_dir =  Path(str(AbsoluteFolderPath(node_link="releases/models")))  # Path(__file__).parent 
        
        
        # Load Kubernetes config
        config.load_kube_config()  # Use config.load_incluster_config() if running inside a cluster
        self.kclient = client.CoreV1Api()


        # Call the update logic during initialization
        self.__call__()

    def apply(self):
        """
        Applies all model deployment manifests in `releases/models` folder 
        """
        command = ["kubectl", "apply", "-f", str(self.model_dir) + "/" ]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            release_yamls = [str(x).split("/")[-1] for x in list(self.model_dir.iterdir())]
            print("Output:", result.stdout)
            print(f"\n\nSuccessfully released model: {release_yamls}\n\n")
        else:
            release_yamls = [str(x).split("/")[-1] for x in list(self.model_dir.iterdir())]
            print(f"Failed to apply resources. Found deployment manifest: {release_yamls}")
            print("Error:", result.stderr)
 
    def delete(self):
        """
        Deletes Kubernetes resources using `kubectl delete -f`.
        """
        command = ["kubectl", "delete", "-f", str(self.model_dir) + "/"]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0:
            deleted_release_yamls = [str(x).split("/")[-1] for x in list(self.model_dir.iterdir())]
            print(f"Successfully deleted model release: {deleted_release_yamls}")
            print("Output:", result.stdout)
            print("Deleting manifest files ...")
            [x.unlink() for x in list(self.model_dir.iterdir())]
        else:
            deleted_release_yamls = list(self.model_dir.iterdir())
            print(f"Failed to delete model release: {deleted_release_yamls}")
            print("Error:", result.stderr)
    
    def __call__(self):
        """
        Adds or removes an entry from the predictor_servers dictionary in the Seldon Core ConfigMap.
        """
        # Fetch the existing ConfigMap
        cm_name = "seldon-config"
        namespace = "seldon-system"
        try:
            cm = self.kclient.read_namespaced_config_map(cm_name, namespace)
        except ApiException as e:
            print(f"Failed to fetch ConfigMap: {e}")
            return

        # Parse the predictor_servers data
        predictor_servers = json.loads(cm.data["predictor_servers"])

        if self.add:
            # Add a new entry to the predictor_servers dictionary
            new_entry = {
                "protocols": {
                    "v2": {
                        "image": self.img_name,
                        "defaultImageVersion": self.tag
                    }
                }
            }
            predictor_servers[self.server_name] = new_entry
            print(f"Added entry for {self.server_name} to predictor_servers.")
            self.apply()


        elif self.remove:
            # Remove the entry from the predictor_servers dictionary
            if self.server_name in predictor_servers:
                del predictor_servers[self.server_name]
                print(f"Removed entry for {self.server_name} from predictor_servers.")
                self.delete()
            else:
                print(f"Entry {self.server_name} not found in predictor_servers.")
                self.delete()

        # Update the ConfigMap with the modified predictor_servers
        cm.data["predictor_servers"] = json.dumps(predictor_servers, indent=4)
        try:
            self.kclient.replace_namespaced_config_map(cm_name, namespace, cm)
            print("ConfigMap updated successfully.")
        except ApiException as e:
            print(f"Failed to update ConfigMap: {e}")



def main():

    # Set up argument parser
    parser = argparse.ArgumentParser(description="Manage Seldon inference servers and model release manifests.")

    parser.add_argument('--image-uri', required=True, help="The image URI (e.g., 'docker.io/akinolawilson/t5-small:fc5e18ab')")
    parser.add_argument('--add', action='store_true', default=False, help="If provided, the inference server will be added to seldon and a model release manifest will be generated. Either --add OR --remove must be provided")
    parser.add_argument('--remove', action='store_true', default=False, help="If provided, the inference server will removed from seldon and the model release manifest will be deleted. Either --remove OR --add must be provided")
    
    args = parser.parse_args()
    assert args.add != args.remove, "Cannot provide none or both the flags `--remove` and `--add`. They are mutually exclusive and one is required"
    # from pprint import pprint
    # pprint(args.__dict__)
    model_name = args.image_uri.split(":")[-1] # The name of the model to generate release manifests 

    # compile model release 
    Compiler(model_name, add=args.add, remove=args.remove)
    # update inference server 
    InferenceServerManager(args.image_uri, add=args.add, remove=args.remove)
    
if __name__ == "__main__":
    main()