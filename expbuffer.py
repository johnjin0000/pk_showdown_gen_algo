import numpy as np

class ExpBuffer():

    def __init__(self, size = 100):
        self.size = size
        self.buffer = []

    # Add to buffer or replace an item randomly if buffer is full
    def add(self, experience):
        if len(self.buffer) >= self.size:
            self.buffer[np.random.randint(len(self.buffer))] = experience
        else:
            self.buffer.append(experience)

    # Randomly select item from buffer
    def sample(self):
        return self.buffer[np.random.choice(self.buffer, size = 1)]
