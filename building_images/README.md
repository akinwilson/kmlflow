# Instructions 
## Localling building and writing images

will build the `Dockerfile` in this directoy and call it `hello` with the tag `latest`
```
docker build . -t hello:latest
```
will run the `hello` image mapping `8989` port of the hostmachine to the port `8950` of the container os. 
Check the `Dockfile` `CMD` section to alter the container port
```
docker run -p 8989:8950 hello 
```
## Pushing images to remote repository

Go to [docker hub](https://hub.docker.com/) you can create a free registry with them. You'll likely be using different registries throughout your endeavour like [Amazon Elastic Container Registry](https://aws.amazon.com/ecr/) but at the end, they all server the purpose of being **image registries** 


change the tag of the image to match that of a private  (you'll need to use `docker login` then, or public repository); `akinwilson/k8s`
```
docker tag hello akinwilson/k8s:latest
```

then transfer or *push* the image to the remote repostory `akinwilson/k8s`
```
docker push akinwilson/k8s:latest
```
you can now run your newly tagged image in `detached mode -d` with a process name of `running_hello`
```
docker run -d --name running_hello -p 8989:8950 akinwilson/k8s:latest
```

**NOTE** it is usual to set up one registry for one purpose such that downstream applications can always rely on the `latest` tag corrsponding to the latests software up and therefore swith images out for one another. 

## Resource allocation 

```
docker run -d --name running_hello -p 8989:8950 --memory 200m --memory-swap 1G --cpu-shares 1024 akinwilson/k8s:latest
```
where: 
- `--memory`  amount of memory the container can have in MegaBytes *MB* 
- `--memory-shap` amount of memory allowed to be swapped to disk. 
- `--cpu-shares` 1024 is the default and lets a single container use the entry CPU. Two containers with this setting on one node then both share **0.5** of the CPU. 