# Creating, maintaining and deleting Pods 

## Imperative creation style 

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

## Declerative creation 

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

## Health checks 
K8s will automatically monitor your application using *process health check*. Insufficient since if your process has a **deadlock** and is unable to to serve requests, a *process health check* will suggest nothing is wrong. K8s therefore introduced a **liveness** health check. This **liveness** health check checks for application-specific signs of functioning. You will need to add an *endpoint* to your containerised application to handle this liveness probe, and update the manifest.yaml to reflect this liveness prob. Like this: 

```
@app.get('/healthy')
async def liveness():
    logger.info("Livenesss health check made")
    return {"message": "The server is alive and functioning as expected"}
```
you will then need to update the pods manifest file to reflect where this liveness probe can be made to. **NOTICE** the `/healthy` port corresponds to the internal port we are running our application at, not the port docker forwards incoming connection from to. 

```
apiVersion: v1
kind: Pod 
metadata: 
  name: hello
spec:
  containers:
  - image: akinwilson/k8s:latest
    name: hello
    livenessProbe:
      httpGet:
        path: /healthy
        port: 8950 # notice this is the port that we are running the application internally at 
      initialDelaySeconds: 5
      timeoutSeconds: 1
      periodSeconds: 10
      failureThreshold: 3
    ports:
      - containerPort: 8989
        name: http
        protocol: TCP
```

you will then see in the logs, this healthy endpoint being hit, like this 

```
Every 1.0s: kubectl logs pods/hello                                                                                                                                                               battle-station: Sat Dec  7 11:02:16 2024

INFO:     Tester application has started
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8950 (Press CTRL+C to quit)
INFO:     Livenesss health check made  <------- CHECK MADE EVERY 10 seconds
INFO:     10.244.0.1:55638 - "GET /healthy HTTP/1.1" 200 OK
```

## Resource Management 
Large variation in notation for resource-allowance specification 
- **Memory**: PB,GB,KB and PiB, GiB, KiB; former base 2 and later base 10. 1MB, would allocate 1024 Kilobytes to the application. 
- **Compute**: millicores, e.g. 100 millicores would be a 10% of a CPU's core to application 

we can specfiy this resource allocation in our manifest file, both the **requested** amounts, and the top **limits** of the possibly allocated resources.  

```
apiVersion: v1
kind: Pod 
metadata: 
  name: hello
spec:
  containers:
  - image: akinwilson/k8s:latest
    name: hello
    resources:
      requests:
        cpu: "100m" # half a core minimum to application 
        memory: "128Mi" # 128MB of memory min dedicated to application 
      limits:
        cpu: "500m" # a core maximium dedicated to application 
        memory: "256Mi" # 128MB of memory max dedicated to application 
    livenessProbe:
      httpGet:
        path: /healthy
        port: 8950 # notice this is the port that we are running the application internally at 
      initialDelaySeconds: 5
      timeoutSeconds: 1
      periodSeconds: 10
      failureThreshold: 3
    ports:
      - containerPort: 8989
        name: http
        protocol: TCP
```
## Persisting data with volumes 

For a cluster created with *kind*, we neee to ahead of the cluster creation, specify mounts. Hence, for this demonstration, this will be omitted. But the manifest file to create such a cluster can be found in this directory. 


To make a *post* to our endpoint in order to save data to our presistent volumne, we can use the `curl` command to encode a post request to our endpoint 
```
curl -v -H "Content-Type: application/json" -X POST \
     -d '{"message":"testing presistent storage"}' http://127.0.0.1:8989/volumes/
Note: Unnecessary use of -X or --request, POST is already inferred.
```
although this is meant to appear in the local directory `/data`, the volumes do not work as expected with `kind`.

You can check though that the post requests are being recorded through interactively investigating the pod. 

```
➜  1building_images git:(main) ✗ kubectl exec -it hello -- sh
# ls
__pycache__  data  requirements.txt  server.py
# cd data
# ls      
testing.txt
# cat testing.txt
testing presistent storage1
testing presistent storage2
# 
```
where these two records we expect to have appear across the volumes.