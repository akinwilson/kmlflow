#!/bin/sh

GREEN='\033[0;32m'
LIGHTPURPLE='\033[1;35m'
LIGHTCYAN='\033[1;36m'
YELLOW='\033[1;33m'
# reset
RESET='\033[0m'


project_title=$(cat <<"EOF"

 _              _  __ _               
| | ___ __ ___ | |/ _| | _____      __
| |/ / '_ ` _ \| | |_| |/ _ \ \ /\ / /
|   <| | | | | | |  _| | (_) \ V  V / 
|_|\_\_| |_| |_|_|_| |_|\___/ \_/\_/  


EOF
)


echo "\n\n${YELLOW}${project_title}${RESET}\n\n"


# Verify that appropriate tools are installed.
if [ -z "$(command -v docker)" ]; then
  echo "Unable to find Docker"
  echo "To install Docker, please follow this guide: ${GREEN}https://docs.docker.com/get-docker${RESET}"
  exit 1
fi

if [ -z "$(command -v nvidia-container-toolkit)" ]; then
  echo "Unable to find NVIDIA container toolkit"
  echo "To install the NVIDIA container toolkit, please follow this guide: ${GREEN}https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html${RESET}"
  exit 1 
fi


# Path to the daemon.json file
DAEMON_JSON_PATH="/etc/docker/daemon.json"

# Expected content (multi-line format)
EXPECTED_CONTENT='{
    "runtimes": {
        "nvidia": {
            "args": [],
            "path": "nvidia-container-runtime"
        }
    }
}'

# Read the actual content of the daemon.json file
ACTUAL_CONTENT=$(cat "$DAEMON_JSON_PATH")

# Use diff to compare the actual content with the expected content
echo "$EXPECTED_CONTENT" > /tmp/expected_daemon.json
echo "$ACTUAL_CONTENT" > /tmp/actual_daemon.json

if diff -u /tmp/expected_daemon.json /tmp/actual_daemon.json > /dev/null; then
    echo "Cluster will have GPU access through containers "
else
    echo "You have not configured nvidia-container-runtime to be used by docker. You will not have GPU access"
    echo "Revisit ${GREEN}https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html${RESET} to finish the configuration."
fi
# Clean up temporary files
rm /tmp/expected_daemon.json /tmp/actual_daemon.json


# check minIO client exits 
if [-z "$(command -v mc)" ]; then 
  echo "Unable to find minio client"
  echo "To install the minio client, please follow this guide: ${GREEN}https://min.io/docs/minio/linux/reference/minio-mc.html${RESET}"
  echo "You do not necessary need it, but it allows you to communicate with your MinIO server through the CLI"
fi 

# check yaml processor is install  
if [-z "$(command -v yq)" ]; then 
  echo "Unable to find YAML inline processor"
  echo "To install the yq, please follow this guide: ${GREEN}https://github.com/mikefarah/yq${RESET}"
  exit 1 
fi 


# check if minikube exists
if [ -z "$(command -v minikube)" ]; then
  echo "Unable to find Minikube"
  echo "To install Minikube, please follow this guide: ${GREEN}https://k8s-docs.netlify.app/en/docs/tasks/tools/install-minikube/${RESET}"
  exit 1
fi

if [ -z "$(command -v kubectl)" ]; then
  echo "Unable to find kubectl"
  echo "To install kubectl, please follow this guide: ${GREEN}https://kubernetes.io/docs/tasks/tools/#kubectl${RESET}"
  exit 1
fi

echo "\nYou have all CLI tools required, ready for ${LIGHTPURPLE}local deployment${RESET} of ${YELLOW}kmlflow${RESET}\n\n"
