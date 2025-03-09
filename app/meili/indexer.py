import kubernetes
from kubernetes import client, config
import meilisearch
import json
import mlflow
import requests
import os

# Meilisearch configuration
MEILISEARCH_HOST = os.environ.get(
    "MEILISEARCH_HOST", "http://meilisearch.search.svc.cluster.local:7700"
)
MEILISEARCH_API_KEY = os.environ.get("MEILISEARCH_API_KEY", "your-meilisearch-api-key")
# Grafana configuration
GRAFANA_URL = os.environ.get(
    "GRAFANA_URL", "http://grafana.grafana.svc.cluster.local:3000"
)
GRAFANA_API_KEY = os.environ.get("GRAFANA_API_KEY", "your-grafana-api-key")
headers = {"Authorization": f"Bearer {GRAFANA_API_KEY}"}

meili_client = meilisearch.Client(MEILISEARCH_HOST, MEILISEARCH_API_KEY)


# Kubernetes configuration
config.load_incluster_config()  # Use in-cluster config when deployed in Kubernetes
katib_client = client.CustomObjectsApi()


class Indexer:
    def __init__(self, katib_client=katib_client, meili_client=meili_client):
        self.c = meili_client
        self.kc = katib_client
        self()

    def katib_experiments(self):
        index = self.c.index("katib_experiments")
        try:
            experiments = self.kc.list_cluster_custom_object(
                group="kubeflow.org",
                version="v1beta1",
                plural="experiments",
            )

            documents = []
            for item in experiments["items"]:
                document = {
                    "name": item["metadata"]["name"],
                    "namespace": item["metadata"]["namespace"],
                    "uid": item["metadata"]["uid"],
                    "creationTimestamp": item["metadata"]["creationTimestamp"],
                    "status": item["status"],
                    "spec": item["spec"],
                }
                documents.append(document)

            if documents:
                index.add_documents(documents)
                print("Katib experiments indexed successfully.")
            else:
                print("No Katib experiments found.")

        except Exception as e:
            print(f"Error indexing Katib experiments: {e}")

    def grafana_dashboards(
        self,
    ):
        index = self.index("observability")
        try:
            response = requests.get(f"{GRAFANA_URL}/api/search", headers=headers)
            response.raise_for_status()
            dashboards = response.json()

            documents = []
            for dashboard in dashboards:
                document = {
                    "uid": dashboard["uid"],
                    "title": dashboard["title"],
                    "type": dashboard["type"],
                    "url": dashboard["url"],
                    "tags": dashboard["tags"],
                }
                documents.append(document)

            if documents:
                index.add_documents(documents)
                print("Grafana dashboards indexed successfully.")
            else:
                print("No Grafana dashboards found.")

        except requests.exceptions.RequestException as e:
            print(f"Error fetching Grafana data: {e}")
        except Exception as e:
            print(f"Error indexing Grafana dashboards: {e}")

    def mlflow_records(self):
        index = self.c.index("Experiment-tracking")
        mlflow.set_tracking_uri(
            os.getenv("MLFLOW_TRACKING_URI", "http://192.168.58.2/mlflow")
        )

        # Get all runs
        runs = mlflow.search_runs("mlflow_runs")

        # Index runs in Meilisearch
        for run in runs:
            run_data = {
                "run_id": run.info.run_id,
                "experiment_id": run.info.experiment_id,
                "experiment_name": mlflow.get_experiment(run.info.experiment_id).name,
                "start_time": run.info.start_time,
                "status": run.info.status,
                "params": run.data.params,
                "metrics": run.data.metrics,
                # Add other relevant fields
            }
            index.add_documents([run_data])

        print("MLflow data indexed successfully.")

    def __call__(
        self,
    ):
        self.katib_experiments()
        self.grafana_dashboards()
        self.mlflow_records()


if __name__ == "__main__":
    print("Indexing Grafana, Katib and MLFlow for Meili search ... ")
    Indexer()


# katib_experiments()
# index = client.index("observability")
# grafana_dashboards()
# index = client.index("Experiment-tracking")
# mlflow_records()
