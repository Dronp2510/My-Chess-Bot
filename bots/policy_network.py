import torch.nn as nn


class PolicyNetwork(nn.Module):

    def __init__(
        self,
        num_moves
    ):

        super().__init__()

        self.features = nn.Sequential(

            nn.Conv2d(
                12,
                64,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.Conv2d(
                64,
                128,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),

            nn.Conv2d(
                128,
                128,
                kernel_size=3,
                padding=1
            ),

            nn.ReLU(),
        )

        self.policy_head = nn.Sequential(

            nn.Flatten(),

            nn.Linear(
                128 * 8 * 8,
                512
            ),

            nn.ReLU(),

            nn.Dropout(
                0.3
            ),

            nn.Linear(
                512,
                num_moves
            )
        )

    def forward(
        self,
        x
    ):

        x = self.features(x)

        return self.policy_head(x)