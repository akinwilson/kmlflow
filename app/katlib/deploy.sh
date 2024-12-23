set -e 

# 
echo "Deploying local mulit-node kubernetes cluster using kind ..."
kind create cluster --config kind_cluster_deployment.yaml || 


# 
echo "Setting context for kubectl cli tool ..."
kubectl cluster-info --context kind-kf-cluster

echo "Rolling out presistent volume and presistent volume claim for Katlib to use as backend storage ..."
kubectl apply -f presistent_volume_and_claim.yaml 

echo "Rolling out cluster dashboard application ... "
kubectl apply -f dashboard.yaml

echo "Creating Service Account ...."
kubectl apply -f admin.yaml

echo "Allow all service accounts to view all resources .. "
kubectl apply -f permissions.yaml


echo "Install Katlib ..."
kubectl apply -k "github.com/kubeflow/katib.git/manifests/v1beta1/installs/katib-standalone?ref=master"

echo "Set up proxy server to make cluster dashboard available ..."
kubectl proxy & 

echo ""
echo "Creating access token ..."
echo ""
kubectl create token user 


echo ""
echo "Head to:\n\nhttp://localhost:8001/api/v1/namespaces/kubernetes-dashboard/services/https:kubernetes-dashboard:/proxy/\n\nto view the k8s cluster health\n\n"


echo "To access the katlib's user interface"

kubectl port-forward svc/katib-ui -n kubeflow 8080:80 &
 
echo "Accessing the UI through:\n\n"
echo "http://localhost:8080/katib/"