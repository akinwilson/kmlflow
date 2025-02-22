# Kmlflow unified UI

## Overview 
Each service deployed to the cluster, where necessary, has its on ingress associated to make it accessible outside the cluster. To make the experience of viewing the various web UIs more streamlined, this Django application server provides a unified web UI experience to the platform, rather than having the hop between the various services  viewed through different tabs in the browser. 


## Development
For local development, install the requirements 
```bash
pip install -r requirements.txt 
```
To run the server in development mode with hot-reloading, run 
```bash 
python manage.py runserver 127.0.0.1:8000
```
