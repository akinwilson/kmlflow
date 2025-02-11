#!/bin/bash 
docker run --rm --gpus all nvidia/cuda:11.0.3-base-ubuntu20.04 nvidia-smi

# installing device plugin for nvidia 

kubectl create -f https://raw.githubusercontent.com/NVIDIA/k8s-device-plugin/v0.10.0/nvidia-device-plugin.yml


# test gpu image 
kubectl run gpu-check -it --rm --image=nvidia/cuda:11.0.3-base-ubuntu20.04 --overrides='
{
  "apiVersion": "v1",
  "kind": "Pod",
  "metadata": {
    "name": "gpu-check"
  },
  "spec": {
    "tolerations": [
      {
        "key": "node-role.kubernetes.io/control-plane",
        "operator": "Exists",
        "effect": "NoSchedule"
      }
    ],
    "containers": [
      {
        "name": "gpu-check",
        "image": "nvidia/cuda:11.0.3-base-ubuntu20.04",
        "command": ["/bin/bash"],
        "resources": {
          "limits": {
            "nvidia.com/gpu": 1
          }
        }
      }
    ]
  }
}'