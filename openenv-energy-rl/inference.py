from environment import EnergyEnv
from stable_baselines3 import PPO


def main():
    env = EnergyEnv()
    model = PPO("MlpPolicy", env, verbose=1)
    model.learn(total_timesteps=10000)

    obs = env.reset()
    done = False
    step = 0
    while not done:
        action, _states = model.predict(obs)
        obs, reward, done, info = env.step(action)
        step += 1
        print(f"Action: {int(action)} | Reward: {reward:.2f} | State: {obs.tolist()}")


if __name__ == "__main__":
    main()
