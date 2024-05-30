import torch
from torch import nn

###########################################################
# Choices for classification head
###########################################################

class ClanLSTM(nn.Module):

    def __init__(self, embed_dim, output_dim):
        super().__init__()

        self.lstm = nn.LSTM(embed_dim, embed_dim, bidirectional=True)

        self.linear_stack = nn.Sequential(
            nn.Linear(2*embed_dim, 4*embed_dim), # Everything x2 because biLSTM
            nn.ReLU(),
            nn.LayerNorm(4*embed_dim),
            nn.Linear(4*embed_dim, 4*embed_dim), # Everything x2 because biLSTM
            nn.ReLU(),
            nn.LayerNorm(4*embed_dim),
            nn.Linear(4*embed_dim, output_dim)
        )

    def forward(self, x):

        x, _ = self.lstm(x)
        x = self.linear_stack(x)

        return x

    def embed(self, x):

        x, _ = self.lstm(x)

        return x

class FamLSTM(nn.Module): 
    def __init__(self, embed_dim, maps, device):
        super().__init__()
        self.clan_fam_matrix = maps['clan_family_matrix'].to(device)
        self.f = self.clan_fam_matrix.shape[1]

        self.lstm = nn.LSTM(embed_dim, embed_dim, bidirectional=True)

        self.linear_stack = nn.Sequential(
            nn.Linear(2*embed_dim, 4*embed_dim), # Everything x2 because biLSTM
            nn.ReLU(),
            nn.LayerNorm(4*embed_dim),
            nn.Linear(4*embed_dim, 4*embed_dim), # Everything x2 because biLSTM
            nn.ReLU(),
            nn.LayerNorm(4*embed_dim),
            nn.Linear(4*embed_dim, self.f)
        )

    def forward(self, x,x_c):
        # Generate clan to fam weights
        weights = torch.matmul(x_c, self.clan_fam_matrix)

        # Get fam logits
        x, _ = self.lstm(x)
        x = self.linear_stack(x)

        # elementwise multiplication of weights and fam_vectors
        weighted_fam_vectors = x * weights

        return weighted_fam_vectors, x