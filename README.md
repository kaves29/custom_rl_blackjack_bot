# Blackjack Reinforcement Learning

## 1. About the Project

I built this project to test how reinforcement learning can be used to learn blackjack strategies. I first created the blackjack game itself in Python, including the deck, cards, player, dealer, hands, betting, doubling, splitting, and round settlement. I then turned the game into a Gymnasium reinforcement learning environment so that different agents could interact with it.

The main goal was to compare three different approaches:

- Random Agent
- DQN
- PPO

The Random Agent acts as a baseline, while DQN and PPO are trained to learn their own strategies through repeated gameplay.

## 2. Environment and Reinforcement Learning

The project uses Python, Gymnasium, NumPy, SciPy, and Stable-Baselines3.

The agent receives information that a real blackjack player would be able to see, including:

- Current hand cards
- Current hand value
- Whether the hand is soft
- Dealer's visible card
- Current wager
- Bankroll
- Hand win rate
- Number of rounds played

The agent has four possible actions:

```text
0 = Hit
1 = Stand
2 = Double
3 = Split

**You are also able to play blackjack if you please by running the game.py file :)**