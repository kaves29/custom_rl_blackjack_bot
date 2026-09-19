from stable_baselines3 import DQN
from stable_baselines3.common.env_checker import check_env
from env import BlackjackEnvironment
import config as cfg

# Train DQN model on custom Blackjack environment
env = BlackjackEnvironment(cfg.random_starter_money)
check_env(env)

model = DQN("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=cfg.dqn_total_train_steps, 
            log_interval=cfg.dqn_log_interval,
            progress_bar=True
            )

model.save("DQN_blackjack_bot")

# Test DQN model on custom Blackjack environment
model = DQN.load("DQN_blackjack_bot")
num_eval_episodes = 100

bankrolls = []
rounds = []
win_rates = []
for episode_idx in range(num_eval_episodes):
    observation, info = env.reset()

    while True:
        action, _states = model.predict(observation, deterministic=True)
        observation, reward, terminated, truncated, info = env.step(action)

        if terminated or truncated:
            break

    bankrolls.append(env.player.player_money)
    rounds.append(env.round_counter)
    win_rates.append(env.win_counter / env.total_hands)

print("Average bankroll:", sum(bankrolls) / len(bankrolls))
print("Average rounds:", sum(rounds) / len(rounds))
print("Average win rate:", sum(win_rates) / len(win_rates))