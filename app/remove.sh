set -e 

echo "Deleting cluster ..."
kind delete cluster

echo "Delete cluster context from kubectl ..."
# Need to replace cluster name with env variable here
kubectl config delete-cluster kind-kmflow-local-v1

echo "Using docker client to remove cluster processes ... "
docker stop $(docker ps -a -q)


echo "Removing images ... "
docker rmi -f $(docker images -aq)

echo "Removing kind network"
docker network rm kind 
