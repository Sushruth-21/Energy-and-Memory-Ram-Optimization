import gym
import numpy as np


class EnergyEnv(gym.Env):
    def __init__(self):
        super(EnergyEnv, self).__init__()
        self.state = [50.0, 5.0]  # [RAM usage %, electricity kWh]
        self.action_space = gym.spaces.Discrete(3)  # 0=do nothing, 1=reduce RAM, 2=reduce electricity
        self.observation_space = gym.spaces.Box(low=0.0, high=100.0, shape=(2,), dtype=np.float32)

    def reset(self):
        self.state = [50.0, 5.0]
        return np.array(self.state, dtype=np.float32)

    def step(self, action):
        ram, elec = self.state
        if action == 1:
            ram = max(0.0, ram - 5.0)
        elif action == 2:
            elec = max(0.0, elec - 1.0)

        reward = -(ram / 100.0 + elec / 10.0)
        done = ram <= 0.0 or elec <= 0.0
        self.state = [ram, elec]

        return np.array(self.state, dtype=np.float32), reward, done, {}

    def render(self, mode="human"):
        print(f"RAM: {self.state[0]:.1f}%, Electricity: {self.state[1]:.1f} kWh")
