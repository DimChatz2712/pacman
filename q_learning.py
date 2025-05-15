import random
import numpy as np

class QAgent:
    def __init__(self, num_states, num_actions, α=0.1, γ=0.9, ϵ=0.2):
        self.Q = np.zeros((num_states, num_actions))
        self.alpha = α      # Δείκτης μάθησης
        self.gamma = γ      # Συντελεστής discount 
        self.epsilon = ϵ    # Δείκτης εξερεύνησης

    def choose_action(self, s):
        
        if random.random() < self.epsilon:
            return random.randrange(self.Q.shape[1])
        return int(np.argmax(self.Q[s]))

    def learn(self, s, a, r, s2):
        
        best_next = np.max(self.Q[s2])
        self.Q[s, a] += self.alpha * (r + self.gamma * best_next - self.Q[s, a])


