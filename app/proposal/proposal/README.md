# Kmlflow unified UI

## Overview 
Each service deployed to the cluster, where necessary, has its on ingress associated to make it accessible outside the cluster. To make the experience of viewing the various web UIs more streamlined, this Django application server provides a unified web UI experience to the platform, rather than having the hop between the various services  viewed through different tabs in the browser. 


## Development
For local development, create a python virtual environment and install the requirements 
```bash
pip install -r dev.requirements.txt 
```
Create the database schemas and apply them to the DB
```bash
python manage.py makemigrations && python manage.py migrate 
```

Populating the dev database
```bash
python manage.py loaddata ./proposals/fixtures/current_proposals.json
```
generating proposal categories and tags objects in database and assigning random selection of tags to proposals

```bash
python manage.py load_tags && python manage.py assign_tags
```



To run the server in development mode with hot-reloading, run 
```bash 
python manage.py runserver 127.0.0.1:8000
```
