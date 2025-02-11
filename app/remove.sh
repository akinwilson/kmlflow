#!/usr/bin/env bash

set -e

# Default cluster name, can be overridden by environment variable
DEFAULT_CLUSTER_NAME="kmlflow-local-v1"
CLUSTER_NAME="${CLUSTER_NAME:-$DEFAULT_CLUSTER_NAME}"

echo "Using cluster name: $CLUSTER_NAME"

echo "Deleting cluster ..."
minikube delete


# echo "Delete cluster context from kubectl ..."
# kubectl config delete-cluster "kind-$CLUSTER_NAME"

# echo "Using Docker client to remove cluster processes ..."
# docker stop $(docker ps -a -q --filter "name=$CLUSTER_NAME")

# echo "Removing images ..."
# docker rmi -f $(docker images -aq)

# # Avoid removing the volume directory for persisting data
# echo "Removing kind network ..."
# docker network rm kind

# echo "Destroy script complete!"

