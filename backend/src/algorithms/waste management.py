# waste_management_rl.py
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
from collections import deque
import matplotlib.pyplot as plt
from datetime import datetime

# Environment Constants
ZONES = 10
MAX_WASTE = 1000  # kg per zone
TRUCK_CAPACITY = 5000  # kg
FUEL_CAPACITY = 1000
DAILY_WASTE_GEN = [50, 150]  # min/max waste generation per zone

# PPO Hyperparameters
LEARNING_RATE = 0.0003
GAMMA = 0.99
EPS_CLIP = 0.2
K_EPOCHS = 4
BUFFER_SIZE = 2000
BATCH_SIZE = 64
ENTROPY_COEF = 0.01

class WasteEnvironment:
    def __init__(self):
        self.zones = ZONES
        self.reset()
        
    def reset(self):
        self.waste_levels = np.random.randint(100, 300, size=self.zones)
        self.truck = {
            'capacity': TRUCK_CAPACITY,
            'load': 0,
            'fuel': FUEL_CAPACITY,
            'position': 0
        }
        self.day = 0
        self.overflow_penalties = 0
        return self._get_state()
    
    def _get_state(self):
        return np.concatenate((
            self.waste_levels / MAX_WASTE,
            [self.truck['load'] / TRUCK_CAPACITY,
             self.truck['fuel'] / FUEL_CAPACITY,
             self.truck['position'] / self.zones]
        ))
    
    def _generate_daily_waste(self):
        self.waste_levels += np.random.randint(
            DAILY_WASTE_GEN[0],
            DAILY_WASTE_GEN[1]+1,
            size=self.zones
        )
        self.waste_levels = np.clip(self.waste_levels, 0, MAX_WASTE)
    
    def step(self, action):
        done = False
        reward = 0
        
        # Action interpretation
        target_zone = action % self.zones
        collect_amount = (action // self.zones + 1) * 100  # 100-500 kg
        
        # Calculate fuel cost
        distance = abs(target_zone - self.truck['position'])
        fuel_cost = distance * 2
        if self.truck['fuel'] < fuel_cost:
            reward -= 50
            return self._get_state(), reward, done, {}
        
        # Update position and fuel
        self.truck['position'] = target_zone
        self.truck['fuel'] -= fuel_cost
        
        # Collection logic
        collectable = min(
            collect_amount,
            self.waste_levels[target_zone],
            self.truck['capacity'] - self.truck['load']
        )
        self.waste_levels[target_zone] -= collectable
        self.truck['load'] += collectable
        
        # Reward components
        reward += collectable * 0.5
        reward -= fuel_cost * 0.1
        
        # Overflow penalties
        overflow = self.waste_levels - MAX_WASTE
        overflow_penalty = np.sum(overflow[overflow > 0]) * 0.2
        reward -= overflow_penalty
        self.overflow_penalties += overflow_penalty
        
        # Daily updates
        self._generate_daily_waste()
        self.day += 1
        
        # Terminal conditions
        if self.day >= 30 or self.overflow_penalties > 1000:
            done = True
            reward -= 200 if self.overflow_penalties > 1000 else 0
            
        return self._get_state(), reward, done, {}

class ActorCritic(nn.Module):
    def __init__(self, state_dim, action_dim):
        super(ActorCritic, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU()
        )
        self.actor = nn.Linear(256, action_dim)
        self.critic = nn.Linear(256, 1)
        
    def forward(self, x):
        x = self.fc(x)
        return self.actor(x), self.critic(x)

class PPOAgent:
    def __init__(self, state_dim, action_dim):
        self.policy = ActorCritic(state_dim, action_dim)
        self.optimizer = optim.Adam(self.policy.parameters(), lr=LEARNING_RATE)
        self.buffer = deque(maxlen=BUFFER_SIZE)
        self.MseLoss = nn.MSELoss()
        
    def select_action(self, state):
        state = torch.FloatTensor(state).unsqueeze(0)
        with torch.no_grad():
            logits, value = self.policy(state)
        dist = Categorical(logits=logits)
        action = dist.sample()
        return action.item(), dist.log_prob(action), value.squeeze()
    
    def update(self):
        if len(self.buffer) < BATCH_SIZE:
            return
        
        # Sample batch
        batch = random.sample(self.buffer, BATCH_SIZE)
        states, actions, old_log_probs, rewards, next_states, dones = zip(*batch)
        
        # Convert to tensors
        states = torch.FloatTensor(states)
        actions = torch.LongTensor(actions)
        old_log_probs = torch.FloatTensor(old_log_probs)
        rewards = torch.FloatTensor(rewards)
        next_states = torch.FloatTensor(next_states)
        dones = torch.FloatTensor(dones)
        
        # Calculate advantages
        with torch.no_grad():
            _, next_values = self.policy(next_states)
            td_targets = rewards + (1 - dones) * GAMMA * next_values
            values = self.policy(states)[1]
            advantages = td_targets - values
        
        # Optimize policy for K epochs
        for _ in range(K_EPOCHS):
            logits, values = self.policy(states)
            dist = Categorical(logits=logits)
            new_log_probs = dist.log_prob(actions)
            entropy = dist.entropy().mean()
            
            # Ratios
            ratios = (new_log_probs - old_log_probs).exp()
            
            # Surrogate loss
            surr1 = ratios * advantages
            surr2 = torch.clamp(ratios, 1-EPS_CLIP, 1+EPS_CLIP) * advantages
            actor_loss = -torch.min(surr1, surr2).mean() - ENTROPY_COEF * entropy
            critic_loss = self.MseLoss(values, td_targets)
            
            # Total loss
            loss = actor_loss + 0.5 * critic_loss
            
            # Gradient step
            self.optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(self.policy.parameters(), 0.5)
            self.optimizer.step()

class WasteManagementRL:
    def __init__(self):
        self.env = WasteEnvironment()
        self.state_dim = ZONES + 3  # waste levels + truck params
        self.action_dim = ZONES * 5  # 5 collection amounts per zone
        self.agent = PPOAgent(self.state_dim, self.action_dim)
        self.rewards = []
        self.overflow_history = []
        
    def train(self, episodes=1000):
        for ep in range(episodes):
            state = self.env.reset()
            ep_reward = 0
            done = False
            
            while not done:
                action, log_prob, value = self.agent.select_action(state)
                next_state, reward, done, _ = self.env.step(action)
                ep_reward += reward
                
                self.agent.buffer.append((
                    state,
                    action,
                    log_prob,
                    reward,
                    next_state,
                    done
                ))
                
                state = next_state
                self.agent.update()
                
            self.rewards.append(ep_reward)
            self.overflow_history.append(self.env.overflow_penalties)
            
            if ep % 50 == 0:
                avg_reward = np.mean(self.rewards[-50:])
                print(f"Episode {ep}, Avg Reward: {avg_reward:.2f}")
                
        self._save_model()
        self._plot_progress()
    
    def _save_model(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        torch.save(self.agent.policy.state_dict(), f"waste_model_{timestamp}.pth")
        print("Model saved successfully.")
    
    def _plot_progress(self):
        plt.figure(figsize=(12, 6))
        plt.subplot(1, 2, 1)
        plt.plot(self.rewards)
        plt.title("Training Rewards")
        plt.subplot(1, 2, 2)
        plt.plot(self.overflow_history)
        plt.title("Waste Overflow Penalties")
        plt.tight_layout()
        plt.savefig("training_progress.png")
        plt.show()

if __name__ == "__main__":
    rl_system = WasteManagementRL()
    rl_system.train(episodes=1000)