"""Mock selective machine-unlearning engine used by ForgetMe.AI.

IMPORTANT FOR JUDGES:
This is a mathematical demonstration, not a claim that a production LLM's
weights have been irreversibly scrubbed. Real machine unlearning depends on
the model, training data, architecture, optimizer, and formal evaluation.

We create a tiny PyTorch network and deliberately perform gradient ASCENT on
a synthetic "forget" sample. Normal training minimizes loss:

    theta <- theta - learning_rate * grad(L)

The demo reverses the direction:

    theta <- theta + learning_rate * grad(L_forget)

so the forget-set loss increases while the UI continues to protect unrelated
explicit memories. The result is logged and returned to the frontend as
auditable evidence of the simulated operation.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, asdict
import torch
from torch import nn

@dataclass
class UnlearningResult:
    target: str
    before_loss: float
    after_loss: float
    steps: int
    learning_rate: float
    elapsed_seconds: float
    weight_shift: float
    direction: str = "gradient_ascent"

    def as_dict(self):
        return asdict(self)

class TinyForgetModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(4, 8), nn.Tanh(), nn.Linear(8, 1))

    def forward(self, x):
        return self.net(x)

def run_gradient_ascent(target: str = "selected memory", steps: int = 25, lr: float = 0.035) -> UnlearningResult:
    # Fixed seed makes the hackathon demo reproducible for judges.
    torch.manual_seed(7)
    model = TinyForgetModel()

    # Synthetic feature/label pair stands in for the target token association.
    forget_x = torch.tensor([[0.9, -0.4, 0.7, -0.2]])
    forget_y = torch.tensor([[0.15]])
    loss_fn = nn.MSELoss()

    with torch.no_grad():
        before = loss_fn(model(forget_x), forget_y).item()
        before_vector = torch.cat([p.detach().flatten() for p in model.parameters()])

    started = time.perf_counter()
    for _ in range(steps):
        loss = loss_fn(model(forget_x), forget_y)
        model.zero_grad(set_to_none=True)
        loss.backward()

        # CORE DEMO: gradient ASCENT intentionally increases the target loss.
        with torch.no_grad():
            for parameter in model.parameters():
                if parameter.grad is not None:
                    parameter.add_(lr * parameter.grad)

    with torch.no_grad():
        after = loss_fn(model(forget_x), forget_y).item()
        after_vector = torch.cat([p.detach().flatten() for p in model.parameters()])

    return UnlearningResult(
        target=target,
        before_loss=round(before, 6),
        after_loss=round(after, 6),
        steps=steps,
        learning_rate=lr,
        elapsed_seconds=round(time.perf_counter() - started, 4),
        weight_shift=round(torch.linalg.vector_norm(after_vector - before_vector).item(), 6),
    )
