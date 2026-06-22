from pathlib import Path

import torch

from torch.utils.data import DataLoader

from policy_dataset import (
    MoveVocabulary,
    ChessDataset,
)

from policy_network import (
    PolicyNetwork
)

DATASET_FILE = (
    "training_data/datasets/"
    "move_dataset.jsonl"
)

MODELS_DIR = Path(
    "models"
)

MODELS_DIR.mkdir(
    exist_ok=True
)

device = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)

print(
    "Device:",
    device
)

vocab = MoveVocabulary()

vocab.build(
    DATASET_FILE
)

print(
    "Unique Moves:",
    len(vocab.move_to_idx)
)

vocab.save(
    MODELS_DIR /
    "move_vocab.json"
)

dataset = ChessDataset(
    DATASET_FILE,
    vocab
)

loader = DataLoader(
    dataset,
    batch_size=128,
    shuffle=True,
    num_workers=0
)

model = PolicyNetwork(
    len(vocab.move_to_idx)
)

model.to(device)

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=0.001
)

criterion = (
    torch.nn.CrossEntropyLoss()
)

from bots.training_constants import EPOCHS

for epoch in range(EPOCHS):

    model.train()

    running_loss = 0

    for x, y in loader:

        x = x.to(device)

        y = y.to(device)

        optimizer.zero_grad()

        logits = model(x)

        loss = criterion(
            logits,
            y
        )

        loss.backward()

        optimizer.step()

        running_loss += (
            loss.item()
        )

    print(
        f"Epoch "
        f"{epoch+1}/{EPOCHS}"
        f" Loss={running_loss:.3f}"
    )

torch.save(
    model.state_dict(),
    MODELS_DIR /
    "policy.pt"
)

print(
    "\nSaved policy.pt"
)