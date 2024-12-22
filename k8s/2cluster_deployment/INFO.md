# Kubectl; the k8s client 

## Cluster info

simply diagnostic for cluster 
```
kubectl get componentstatuses
```
and this returns 
```
➜  k8s git:(main) ✗ kubectl get componentstatuses
Warning: v1 ComponentStatus is deprecated in v1.19+
NAME                 STATUS    MESSAGE   ERROR
scheduler            Healthy   ok        
controller-manager   Healthy   ok        
etcd-0               Healthy   ok 
```
These are components that make up **cluster**. 
- ***scheduler*** : places different pods on different nodes 
- ***controller-manager*** :  Runs controllers which ensure realiablity; i.e. for example are all replicas of services heathly and running. 
- ***etcd-0*** : Storage server where all API objects are stored. 

with 
```
kubectl get nodes
```
you can list the nodes you have part of your cluster, with an example output being 

```
➜  k8s git:(main) ✗ kubectl get nodes
NAME                 STATUS   ROLES           AGE   VERSION
kind-control-plane   Ready    control-plane   31h   v1.31.2
```
you can describe individual nodes with:

```
kubectl describe node kind-control-plane
```
returning a host of information about that node:

```
➜  k8s git:(main) ✗ k describe node kind-control-plane
Name:               kind-control-plane
Roles:              control-plane
Labels:             beta.kubernetes.io/arch=amd64
                    beta.kubernetes.io/os=linux
                    kubernetes.io/arch=amd64
                    kubernetes.io/hostname=kind-control-plane
                    kubernetes.io/os=linux
                    node-role.kubernetes.io/control-plane=
Annotations:        kubeadm.alpha.kubernetes.io/cri-socket: unix:///run/containerd/containerd.sock
                    node.alpha.kubernetes.io/ttl: 0
                    volumes.kubernetes.io/controller-managed-attach-detach: true
CreationTimestamp:  Wed, 04 Dec 2024 21:50:08 +0000
Taints:             <none>
Unschedulable:      false
Lease:
  HolderIdentity:  kind-control-plane
  AcquireTime:     <unset>
  RenewTime:       Fri, 06 Dec 2024 05:21:45 +0000
Conditions:
  Type             Status  LastHeartbeatTime                 LastTransitionTime                Reason                       Message
  ----             ------  -----------------                 ------------------                ------                       -------
  MemoryPressure   False   Fri, 06 Dec 2024 05:20:29 +0000   Wed, 04 Dec 2024 21:50:07 +0000   KubeletHasSufficientMemory   kubelet has sufficient memory available
  DiskPressure     False   Fri, 06 Dec 2024 05:20:29 +0000   Wed, 04 Dec 2024 21:50:07 +0000   KubeletHasNoDiskPressure     kubelet has no disk pressure
  PIDPressure      False   Fri, 06 Dec 2024 05:20:29 +0000   Wed, 04 Dec 2024 21:50:07 +0000   KubeletHasSufficientPID      kubelet has sufficient PID available
  Ready            True    Fri, 06 Dec 2024 05:20:29 +0000   Wed, 04 Dec 2024 21:50:28 +0000   KubeletReady                 kubelet is posting ready status
Addresses:
  InternalIP:  172.18.0.2
  Hostname:    kind-control-plane
Capacity:
  cpu:                48
  ephemeral-storage:  960300048Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             131724816Ki
  pods:               110
Allocatable:
  cpu:                48
  ephemeral-storage:  960300048Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             131724816Ki
  pods:               110
System Info:
  Machine ID:                 2a2792694b484209b4e6624c2a3cb2e2
  System UUID:                2f8a99c3-983f-4594-b5fa-8006c4d0141d
  Boot ID:                    c4d32a32-1e20-42b3-b394-4603b954eb58
  Kernel Version:             6.8.0-49-generic
  OS Image:                   Debian GNU/Linux 12 (bookworm)
  Operating System:           linux
  Architecture:               amd64
  Container Runtime Version:  containerd://1.7.18
  Kubelet Version:            v1.31.2
  Kube-Proxy Version:         v1.31.2
PodCIDR:                      10.244.0.0/24
PodCIDRs:                     10.244.0.0/24
ProviderID:                   kind://docker/kind/kind-control-plane
Non-terminated Pods:          (16 in total)
  Namespace                   Name                                                    CPU Requests  CPU Limits  Memory Requests  Memory Limits  Age
  ---------                   ----                                                    ------------  ----------  ---------------  -------------  ---
  kube-system                 coredns-7c65d6cfc9-hxgp8                                100m (0%)     0 (0%)      70Mi (0%)        170Mi (0%)     31h
  kube-system                 coredns-7c65d6cfc9-wrswn                                100m (0%)     0 (0%)      70Mi (0%)        170Mi (0%)     31h
  kube-system                 etcd-kind-control-plane                                 100m (0%)     0 (0%)      100Mi (0%)       0 (0%)         31h
  kube-system                 kindnet-cksd9                                           100m (0%)     100m (0%)   50Mi (0%)        50Mi (0%)      31h
  kube-system                 kube-apiserver-kind-control-plane                       250m (0%)     0 (0%)      0 (0%)           0 (0%)         31h
  kube-system                 kube-controller-manager-kind-control-plane              200m (0%)     0 (0%)      0 (0%)           0 (0%)         31h
  kube-system                 kube-proxy-xk8dx                                        0 (0%)        0 (0%)      0 (0%)           0 (0%)         31h
  kube-system                 kube-scheduler-kind-control-plane                       100m (0%)     0 (0%)      0 (0%)           0 (0%)         31h
  kubernetes-dashboard        dashboard-metrics-scraper-58bddb5984-wgbgr              0 (0%)        0 (0%)      0 (0%)           0 (0%)         37m
  kubernetes-dashboard        kubernetes-dashboard-api-568555bb6f-bfzcl               100m (0%)     250m (0%)   200Mi (0%)       400Mi (0%)     56m
  kubernetes-dashboard        kubernetes-dashboard-auth-798f596df5-b2wwg              100m (0%)     250m (0%)   200Mi (0%)       400Mi (0%)     56m
  kubernetes-dashboard        kubernetes-dashboard-cf5b8fcd-wr295                     0 (0%)        0 (0%)      0 (0%)           0 (0%)         37m
  kubernetes-dashboard        kubernetes-dashboard-kong-57d45c4f69-47k8s              0 (0%)        0 (0%)      0 (0%)           0 (0%)         56m
  kubernetes-dashboard        kubernetes-dashboard-metrics-scraper-df869c886-vlf4m    100m (0%)     250m (0%)   200Mi (0%)       400Mi (0%)     56m
  kubernetes-dashboard        kubernetes-dashboard-web-6ccf8d967-p7q6z                100m (0%)     250m (0%)   200Mi (0%)       400Mi (0%)     56m
  local-path-storage          local-path-provisioner-57c5987fd4-s2h5r                 0 (0%)        0 (0%)      0 (0%)           0 (0%)         31h
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests     Limits
  --------           --------     ------
  cpu                1350m (2%)   1100m (2%)
  memory             1090Mi (0%)  1990Mi (1%)
  ephemeral-storage  0 (0%)       0 (0%)
  hugepages-1Gi      0 (0%)       0 (0%)
  hugepages-2Mi      0 (0%)       0 (0%)
Events:              <none>
```

## Cluster components 

### k8s proxy

Component is responisble for routing network traffic to load-balanced serivces inside the k8s cluster. Proxy must therefore be present on very node; achieved through a ***DaemonSet***
```
kubectl get daemonSet -n kube-system kube-proxy
```
outputting
```
➜  k8s git:(main) ✗ kubectl get daemonSet -n kube-system kube-proxy
NAME         DESIRED   CURRENT   READY   UP-TO-DATE   AVAILABLE   NODE SELECTOR            AGE
kube-proxy   1         1         1       1            1           kubernetes.io/os=linux   31h
```
since we only have one node in our kind cluster. 

### K8s DNS 

Provides naming and discovery for services inside cluster. 

```
kubectl get deployments -n kube-system coredns
```
outputting:
```
➜  k8s git:(main) ✗ kubectl get deployments -n kube-system coredns 
NAME      READY   UP-TO-DATE   AVAILABLE   AGE
coredns   2/2     2            2           31h
```
there is also a *service* performing load-balancing for the DNS server
```
kubectl get services -n kube-system kube-dns 
```
outputting 
```
➜  k8s git:(main) ✗ kubectl get services -n kube-system kube-dns 
NAME       TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)                  AGE
kube-dns   ClusterIP   10.96.0.10   <none>        53/UDP,53/TCP,9153/TCP   31h
```