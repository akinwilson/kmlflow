import torch
from torch import nn
from torch.utils.data import DataLoader
from torchinfo import summary
from torchmetrics import Accuracy
from torchvision import datasets
from torchvision.transforms import ToTensor
from argsparse import ArgumentParser 
import mlflow




class ImageClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = nn.Sequential(
            nn.Conv2d(1, 8, kernel_size=3),
            nn.ReLU(),
            nn.Conv2d(8, 16, kernel_size=3),
            nn.ReLU(),
            nn.Flatten(),
            nn.LazyLinear(10),  # 10 classes in total.
        )

    def forward(self, x):
        return self.model(x)




def train(dataloader, model, loss_fn, metrics_fn, optimizer, epoch):
    """Train the model on a single pass of the dataloader.

    Args:
        dataloader: an instance of `torch.utils.data.DataLoader`, containing the training data.
        model: an instance of `torch.nn.Module`, the model to be trained.
        loss_fn: a callable, the loss function.
        metrics_fn: a callable, the metrics function.
        optimizer: an instance of `torch.optim.Optimizer`, the optimizer used for training.
        epoch: an integer, the current epoch number.
    """
    model.train()
    for batch, (X, y) in enumerate(dataloader):
        X, y = X.to(device), y.to(device)

        pred = model(X)
        loss = loss_fn(pred, y)
        accuracy = metrics_fn(pred, y)

        # Backpropagation.
        loss.backward()
        optimizer.step()
        optimizer.zero_grad()

        if batch % 100 == 0:
            loss, current = loss.item(), batch
            step = batch // 100 * (epoch + 1)
            mlflow.log_metric("loss", f"{loss:2f}", step=step)
            mlflow.log_metric("accuracy", f"{accuracy:2f}", step=step)
            print(f"loss: {loss:2f} accuracy: {accuracy:2f} [{current} / {len(dataloader)}]")





def evaluate(dataloader, model, loss_fn, metrics_fn, epoch):
    """Evaluate the model on a single pass of the dataloader.

    Args:
        dataloader: an instance of `torch.utils.data.DataLoader`, containing the eval data.
        model: an instance of `torch.nn.Module`, the model to be trained.
        loss_fn: a callable, the loss function.
        metrics_fn: a callable, the metrics function.
        epoch: an integer, the current epoch number.
    """
    num_batches = len(dataloader)
    model.eval()
    eval_loss, eval_accuracy = 0, 0
    with torch.no_grad():
        for X, y in dataloader:
            X, y = X.to(device), y.to(device)
            pred = model(X)
            eval_loss += loss_fn(pred, y).item()
            eval_accuracy += metrics_fn(pred, y)

    eval_loss /= num_batches
    eval_accuracy /= num_batches
    mlflow.log_metric("eval_loss", f"{eval_loss:2f}", step=epoch)
    mlflow.log_metric("eval_accuracy", f"{eval_accuracy:2f}", step=epoch)

    print(f"Eval metrics: \nAccuracy: {eval_accuracy:.2f}, Avg loss: {eval_loss:2f} \n")





if __name__ == "__main__":
    


    parser = ArgumentParser()
    parser.add_argument('-lr', '--learning-rate', help="Learning rate for optimisation process, i.e. step size", default=1e-3)
    parser.add_argument('-bs', '--batch-size', help="Sample size of to approximate gradient with during stochastic gradient descent algorithm", default=64)
    parser.add_argument('-e', '--epochs', help="Maxmium number of fitting dataset iterations. I.e. capping the fitting routine", default=10)
    
    parser.add_argument('-t', '--tracking-server-uri', help='Tracking server URI/URL used by client', default='http://localhost:5000')
    parser.add_argument('-ex', '--experiment-name', help='The name to assign to collection of runs making up the experiment.', default='mnist-mini-CNN')
    # Notice we start and experiment, this experiment may have more than one trial/run.  

    args = parser.parse_args()

    # Get cpu or gpu for training.
    device = "cuda" if torch.cuda.is_available() else "cpu"

    training_data = datasets.FashionMNIST(
        root="data",
        train=True,
        download=True,
        transform=ToTensor(),
    )

    test_data = datasets.FashionMNIST(
        root="data",
        train=False,
        download=True,
        transform=ToTensor(),
    )
    print(f"Image size: {training_data[0][0].shape}")
    print(f"Size of training dataset: {len(training_data)}")
    print(f"Size of test dataset: {len(test_data)}")


    train_dataloader = DataLoader(training_data, batch_size=args.batch_size)
    test_dataloader = DataLoader(test_data, batch_size=args.batch_size)


    mlflow.set_tracking_uri(args.tracking_server_uri)
    mlflow.set_experiment(args.experiment_name)


    epochs = 5
    loss_fn = nn.CrossEntropyLoss()
    metric_fn = Accuracy(task="multiclass", num_classes=10).to(device)
    model = ImageClassifier().to(device)
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-3)




    with mlflow.start_run() as run:
        params = {
            "epochs": epochs,
            "learning_rate": 1e-3,
            "batch_size": 64,
            "loss_function": loss_fn.__class__.__name__,
            "metric_function": metric_fn.__class__.__name__,
            "optimizer": "SGD",
        }
        # Log training parameters.
        mlflow.log_params(params)

        # Log model summary.
        with open("model_summary.txt", "w") as f:
            f.write(str(summary(model)))
        mlflow.log_artifact("model_summary.txt")

        for t in range(epochs):
            print(f"Epoch {t+1}\n-------------------------------")
            train(train_dataloader, model, loss_fn, metric_fn, optimizer, epoch=t)
            evaluate(test_dataloader, model, loss_fn, metric_fn, epoch=0)

        # Save the trained model to MLflow.
        mlflow.pytorch.log_model(model, "model")