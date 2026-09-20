from env import BlackjackEnvironment
import config as cfg

env = BlackjackEnvironment(cfg.random_starter_money)

episode_rewards = []
episode_bankrolls = []

for episode_idx in range(cfg.random_num_episodes):
    observation, info = env.reset()
    total_reward = 0

    while True:
        action = env.action_space.sample()
        observation, reward, terminated, truncated, info = env.step(action)
        total_reward += reward

        if terminated or truncated:
            break

    episode_rewards.append(total_reward)
    episode_bankrolls.append(env.player.player_money)

    print(
        f"Episode {episode_idx + 1}: "
        f"Reward = {total_reward}, "
        f"Bankroll = ${env.player.player_money}"
        f"Invalid actions:", env.invalid_action_counter
    )

env.close()