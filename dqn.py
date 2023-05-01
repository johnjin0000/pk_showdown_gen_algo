import torch
from torch import nn
from expbuffer import ExpBuffer

class DQN(nn.Module):
    
    def __init__(self, input_size, hidden_nodes, buffer_size = 100, embedding_dims = 256):
        super().__init__()
        self.layers = nn.Sequential(
            torch.nn.Linear(input_size, hidden_nodes),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_nodes, hidden_nodes // 2),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_nodes // 2, hidden_nodes // 4),
            torch.nn.ReLU(),
            torch.nn.Linear(hidden_nodes // 4, 1)   # Outputs one real number at end
        )
        self.buffer = ExpBuffer(buffer_size)
        self.pokeembed = torch.nn.Embedding(num_embeddings = 72, embedding_dim = embedding_dims)
        self.moveembed = torch.nn.Embedding(num_embeddings = 180, embedding_dim = embedding_dims)
    
    def battle_to_embedding(self, battle):
        pass
    
    def forward(self, x):
        result =  self.layers(x)
        self.buffer.add(x)
        return result
    