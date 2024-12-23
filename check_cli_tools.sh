
# Verify that appropriate tools are installed.
if [ -z "$(command -v docker)" ]; then
  echo "Unable to find Docker"
  echo "To install Docker, please follow this guide: https://docs.docker.com/get-docker"
  exit 1
fi

if [ -z "$(command -v kind)" ]; then
  echo "Unable to find Kind"
  echo "To install Kind, please follow this guide: https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
  exit 1
fi

if [ -z "$(command -v kubectl)" ]; then
  echo "Unable to find kubectl"
  echo "To install kubectl, please follow this guide: https://kubernetes.io/docs/tasks/tools/#kubectl"
  exit 1
fi

echo "You have all CLI tools required, ready to deploy Katlib locally"