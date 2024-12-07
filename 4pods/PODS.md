# Creating, maintaining and deleting Pods 

### Imperative creation style 

creating a pod in the default namespace:
```
kubectl run hello --image=akinwilson/k8s:latest --port=8989
```
you can then see the pod running using 
```
kubectl get pods
```
which returns 
```
➜  k8s git:(main) ✗ k get pods
NAME    READY   STATUS    RESTARTS   AGE
hello   1/1     Running   0          4m18s
```
You can also port-forward to the *pod* directly using: 
```
k port-forward pod/hello 8989:8950
```
or SSH into the one of the containers inside the pod: 

```
kubectl exec -it hello -n default -- sh 
```
To remove the pod:
```
kubectl delete pod hello --now
```

### Declerative creation 

You need the *yaml* file which will look something like this: 

```
apiVersion: v1
kind: Pod 
metadata: 
  name: hello
spec:
  containers:
  - image: akinwilson/k8s:latest
    name: hello
    ports:
      - containerPort: 8989
        name: http
        protocol: TCP
```
and apply it, in a **declerative** manner, using 

```
kubectl apply -f  4pods/pod.yaml
```
you can then see the logs of the container using 
```
watch -n1.0 kubectl logs pod/hello
```
where `watch` allows you to continously see the outputs of the logs. You should expect and output similiar to
```
Every 1.0s: kubectl logs pod/hello                                                                                                                                                                battle-station: Sat Dec  7 10:33:21 2024

INFO:     Tester application has started
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8950 (Press CTRL+C to quit)
INFO:     Hit root URL.
INFO:     127.0.0.1:45330 - "GET / HTTP/1.1" 200 OK
```
you can interactively enter the container inside the pod  using 
```
kubectl exec -it hello -- sh
```
which will place you inside of said container. 


