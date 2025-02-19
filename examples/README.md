## File structure 

```bash 
├── api.py # this is used to publish the serving container in proposal.py and in publish.py.
├── docker
│   ├── Dockerfile.fit # this is the dockerfile which produces akinolawilson/pytorch-train-gpu:latest
│   └── requirements.txt
├── fit.py # training function called to apply hyperparameter optimisation over using the Katib framework. This is the entrypoint to the image akinolawilson/pytorch-train-gpu:latest
├── proposal.py # function proposes an experiment, which is made up of trials 
├── publish.py # example of publishing an serving image using the MLFlow workflow. 
└── track.py # example of tracking an trail of an experiment using the MLFlow framewokr
```