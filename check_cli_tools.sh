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

if [ -z "$(command -v kind)" ]; then
  echo "Unable to find Kind"
  echo "To install Kind, please follow this guide: ${GREEN}https://kind.sigs.k8s.io/docs/user/quick-start/#installation${RESET}"
  exit 1
fi

if [ -z "$(command -v kubectl)" ]; then
  echo "Unable to find kubectl"
  echo "To install kubectl, please follow this guide: ${GREEN}https://kubernetes.io/docs/tasks/tools/#kubectl${RESET}"
  exit 1
fi

echo "\nYou have all CLI tools required, ready for ${LIGHTPURPLE}local deployment${RESET} of ${YELLOW}kmlflow${RESET}\n\n"
