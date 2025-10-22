from __future__ import annotations

import torch
from torch.nn import Module
from torch.utils.data import Dataset, DataLoader

from accelerate import Accelerator

from adam_atan2_pytorch import MuonAdamAtan2

from dreamer4.dreamer4 import (
    VideoTokenizer,
    DynamicsWorldModel
)

# helpers

def exists(v):
    return v is not None

def default(v, d):
    return v if exists(v) else d

def cycle(dl):
    while True:
        for batch in dl:
            yield batch

# trainers

class VideoTokenizerTrainer(Module):
    def __init__(
        self,
        model: VideoTokenizer,
        dataset: Dataset,
        optim_klass = MuonAdamAtan2,
        batch_size = 16,
        learning_rate = 3e-4,
        num_train_steps = 10_000,
        weight_decay = 0.,
        accelerate_kwargs: dict = dict(),
        optim_kwargs: dict = dict(),
        cpu = False,
    ):
        super().__init__()
        self.accelerator = Accelerator(
            cpu = cpu,
            **accelerate_kwargs
        )

        self.model = model
        self.dataset = dataset
        self.train_dataloader = DataLoader(dataset, batch_size = batch_size, drop_last = True, shuffle = True)

        optim_kwargs = dict(
            lr = learning_rate,
            weight_decay = weight_decay
        )

        if optim_klass is MuonAdamAtan2:
            optim = MuonAdamAtan2(
                model.muon_parameters(),
                model.parameters(),
                **optim_kwargs
            )
        else:
            optim = optim_klass(
                model.parameters(),
                **optim_kwargs
            )

        self.optim = optim

        self.num_train_steps = num_train_steps
        self.batch_size = batch_size

        (
            self.model,
            self.train_dataloader,
            self.optim
        ) = self.accelerator.prepare(
            self.model,
            self.train_dataloader,
            self.optim
        )

    @property
    def device(self):
        return self.accelerator.device

    def print(self, *args, **kwargs):
        return self.accelerator.print(*args, **kwargs)

    def forward(
        self
    ):

        iter_train_dl = cycle(self.train_dataloader)

        for _ in range(self.num_train_steps):
            video = next(iter_train_dl)

            loss = self.model(video)
            self.accelerator.backward(loss)

            self.optim.step()
            self.optim.zero_grad()

        self.print('training complete')
