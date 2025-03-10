#!/usr/bin/env python3
import torch

Q = 36028797018963913  # prime within signed64
SEED = 1666
STEPS = 55
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class FiniteFieldLinear(
    torch.nn.ModuleList
):  # over Module which tracks gradients where as ModuleList doesnt
    """
    expect row vector examples
    """

    def __init__(self, d_out, d_in, q=Q, seed=SEED):
        super().__init__()  # Call parent constructor
        self.d_in = d_in
        self.d_out = d_out
        self.q = q

        self.w = torch.randint(0, q, (d_out, d_in), dtype=torch.int64).to(device)
        self.b = torch.randint(0, q, (1, d_out), dtype=torch.int64).to(device)

    def forward(self, x):
        x = x.float()
        w = self.w.float()
        b = self.b.float()
        return ((x @ w.T + b) % self.q).long()

    def __call__(self, x):
        return self.forward(x)


class ModularTanh(torch.nn.ModuleList):
    def __init__(self, q=Q):
        super().__init__()
        self.q = q

    def forward(self, x):
        # Ensure input is within the finite field [0, p-1]
        x = x % self.q
        # Compute tanh-like behavior in the finite field
        # Here, we map x to a range [-k, k] and then apply a modular reduction
        k = self.q // 2  # Midpoint of the field
        x_centered = (x - k) % self.q  # Center around 0 (mod p)
        x = (2 * x_centered) % self.q  # Scale and reduce mod p

        return x

    def __call__(self, x):
        return self.forward(x)


class ModularRNN(torch.nn.ModuleList):

    def __init__(self, d_out, d_in, key, steps=STEPS, activation=ModularTanh(), q=Q):
        super().__init__()
        self.ffl = FiniteFieldLinear(d_out, d_in).to(device)
        self.steps = steps
        self.act = activation
        self.key = key
        self.q = q

    def forward(self, x, participant=["node", "validator"][0]):
        h = x
        if participant == "node":
            for _ in range(self.steps):
                h = self.act(self.ffl(h) + self.key.sk()) % self.q
            return h
        if participant == "validator":
            for _ in range(self.steps):
                # assuming b corresponds to a homomorphic commit vector generated by
                h = self.act(self.ffl(h) + self.b @ self.key.A) % self.q
            return h
