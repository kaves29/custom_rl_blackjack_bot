import gymnasium as gym
import numpy as np
import random
from scipy.stats import truncnorm
import config as cfg
from engine.hand import *


class BlackjackEnvironment(gym.Env):
    def __init__(self, agent_starter_money):
        super().__init__()
        self.starting_bankroll = agent_starter_money
        self.bankroll = agent_starter_money
        self.round_counter = 0
        self.win_counter = 0
        self.total_hands = 0
        self.current_hand_index = 0
        self.invalid_action_counter = 0
        self.total_decisions = 0

        self.action_space = gym.spaces.Discrete(4)
        self.observation_space = gym.spaces.Box(
            low=0,
            high=np.inf,
            shape=(17,),
            dtype=np.float32
        )
        self.round_reward = 0
        self.episode_reward = 0

        self.deck = None
        self.player = None
        self.dealer = None
        self.current_hand = None


    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.bankroll = self.starting_bankroll
        self.round_counter = 0
        self.win_counter = 0
        self.total_hands = 0
        self.current_hand_index = 0
        self.round_reward = 0
        self.episode_reward = 0

        self.deck = Deck([], 1)
        self.deck.create()
        self.player = Player(self.starting_bankroll)
        self.dealer = None
        self.current_hand = None
        inital_wager = self.wager_function()
        self.player.initial_bet(inital_wager)
        player_hand = self.player.hands[0]
        player_hand.cards.extend(self.deck.deal(2))
        self.current_hand = player_hand
        self.dealer = Hand(self.deck.deal(2), 0)

        return self.get_obs(), {}


    def get_obs(self):
        cards = [card.value for card in self.current_hand.cards]

        while len(cards) < 8:
            cards.append(0)

        if self.total_hands == 0:
            win_rate = 0
        else:
            win_rate = self.win_counter / self.total_hands

        can_double = (
            len(self.current_hand.cards) == 2
            and not self.current_hand.finished
            and self.player.player_money >= self.current_hand.wager
        )

        can_split = (
            self.current_hand.is_pair()
            and not self.current_hand.finished
            and not self.current_hand.was_split
            and self.player.player_money >= self.current_hand.wager
        )

        return np.array(
        cards + [
            self.current_hand.hand_value() / 21,
            int(self.current_hand.soft),
            self.dealer.cards[0].value / 11,
            self.current_hand.wager / self.starting_bankroll,
            self.player.player_money / self.starting_bankroll,
            win_rate,
            self.round_counter / 200,
            int(can_double),
            int(can_split)
        ], dtype=np.float32)


    def wager_function(self):
        # Build clipped normal distribution for eplison
        eplison_dist_mean = 0.005
        eplison_dist_sigma = 0.004
        lower_clip = 0.001
        upper_clip = 0.009

        a = (lower_clip - eplison_dist_mean) / eplison_dist_sigma
        b = (upper_clip - eplison_dist_mean) / eplison_dist_sigma
        clipped_dist = truncnorm(a, b, loc=eplison_dist_mean, scale=eplison_dist_sigma) # creating clipped dist

        wager_eplison = clipped_dist.rvs()

        wager = int((cfg.wager_constant + wager_eplison) * self.player.player_money)

        wager = max(1, wager)
        wager = min(wager, int(self.player.player_money))

        return wager


    def update_hand(self):
        for card_idx in range(len(self.player.hands)):
            if not self.player.hands[card_idx].finished:
                self.current_hand_index = card_idx
                self.current_hand = self.player.hands[card_idx]

                return True

        return False


    def dealer_play(self):
        # Dealer play
        self.dealer.hand_value()
        dealer_blackjack = True if self.dealer.hand_value() == 21 else False

        if not dealer_blackjack:
            print("\nDealer's turn.")
            while (self.dealer.hand_value() < 17):
                self.dealer.cards.append(self.deck.draw())

                print("Dealer drew a card!")
                print(f"Dealer is at {self.dealer.hand_value()}")
                if self.dealer.bust:
                    print("Dealer busted!")
                    break
                else:
                    print("Dealer did not bust yet!")

        return self.dealer


    def settle_hand(self):
        outcome = []

        for card_idx in range(len(self.player.hands)):
            self.total_hands += 1
            hand = self.player.hands[card_idx]

            if hand.bust:
                outcome.append("lose")

            elif self.dealer.bust:
                outcome.append("win")
                self.win_counter += 1
                self.player.player_money += hand.wager * 2

            elif hand.blackjack and not self.dealer.blackjack:
                outcome.append("win")
                self.win_counter += 1
                self.player.player_money += hand.wager * 2.5

            elif hand.hand_value() > self.dealer.hand_value():
                outcome.append("win")
                self.win_counter += 1
                self.player.player_money += hand.wager * 2

            elif hand.hand_value() < self.dealer.hand_value():
                outcome.append("lose")

            else:
                outcome.append("tie")
                self.player.player_money += hand.wager

        self.round_counter += 1

        return outcome


    def round_reward_calculation(self, outcome):
        self.round_reward = 0

        for card_idx in range(len(outcome)):
            if outcome[card_idx] == "win":
                if self.player.hands[card_idx].doubled:
                    self.round_reward += 4
                else:
                    self.round_reward += 2

            elif outcome[card_idx] == "lose":
                if self.player.hands[card_idx].doubled:
                    self.round_reward -= 2
                else:
                    self.round_reward -= 1

            elif outcome[card_idx] == "tie":
                self.round_reward += 0

        self.episode_reward += self.round_reward

        return self.round_reward


    def finish_round(self):
        outcome = self.settle_hand()
        reward = self.round_reward_calculation(outcome)

        win_rate = self.win_counter / self.total_hands

        if self.player.player_money < 1:
            reward -= 20
            self.episode_reward -= 20
            return self.get_obs(), reward, True, False, {}

        elif (
            self.round_counter >= 200
            and win_rate > 0.45
            and self.player.player_money >= 2 * self.starting_bankroll
        ):
            reward += 30
            self.episode_reward += 30
            return self.get_obs(), reward, True, False, {}

        self.current_hand_index = 0
        self.round_reward = 0

        self.deck = Deck([], 1)
        self.deck.create()

        self.player.hands = []

        inital_wager = self.wager_function()
        self.player.initial_bet(inital_wager)

        player_hand = self.player.hands[0]
        player_hand.cards.extend(self.deck.deal(2))

        self.current_hand = player_hand
        self.dealer = Hand(self.deck.deal(2), 0)

        return self.get_obs(), reward, False, False, {}


    def finish_invalid_round(self):
        self.round_reward = -1
        self.episode_reward += self.round_reward
        self.round_counter += 1
        self.current_hand_index = 0

        if self.player.player_money < 1:
            self.episode_reward -= 20
            return self.get_obs(), self.round_reward - 20, True, False, {}

        self.round_reward = 0

        self.deck = Deck([], 1)
        self.deck.create()

        self.player.hands = []

        inital_wager = self.wager_function()
        self.player.initial_bet(inital_wager)

        player_hand = self.player.hands[0]
        player_hand.cards.extend(self.deck.deal(2))

        self.current_hand = player_hand
        self.dealer = Hand(self.deck.deal(2), 0)

        return self.get_obs(), -1, False, False, {}


    def step(self, action):
        self.total_decisions += 1

        if action == 0: # Hit
            self.current_hand.cards.append(self.deck.draw())
            hand_value = self.current_hand.hand_value()

            if self.current_hand.bust:
                self.current_hand.finished = True
                new_hand = self.update_hand()

                if(new_hand):
                    print("Moving on to new hand")
                    return self.get_obs(), 0, False, False, {}

                else:
                    print("All hands finished")

                    all_bust = all(hand.bust for hand in self.player.hands)

                    if not all_bust:
                        self.dealer = self.dealer_play()

                    return self.finish_round()

            elif hand_value == 21:
                self.current_hand.finished = True
                new_hand = self.update_hand()

                if(new_hand):
                    print("Moving on to new hand")
                    return self.get_obs(), 0, False, False, {}

                else:
                    print("All hands finished")
                    self.dealer = self.dealer_play()
                    return self.finish_round()

            else:
                observation = self.get_obs()
                return observation, 0, False, False, {}

        elif action == 1: # Stand
            hand_value = self.current_hand.hand_value()
            self.current_hand.finished = True
            
            new_hand = self.update_hand()

            if(new_hand):
                print("Moving on to new hand")
                return self.get_obs(), 0, False, False, {}

            else:
                print("All hands finished")
                self.dealer = self.dealer_play()
                return self.finish_round()

        elif action == 2: # Double
            hand_value = self.current_hand.hand_value()

            if (self.player.double_hand(self.current_hand, self.deck)):
                self.current_hand.finished = True
                
                new_hand = self.update_hand()

                if(new_hand):
                    print("Moving on to new hand")
                    return self.get_obs(), 0, False, False, {}

                else:
                    print("All hands finished")
                    self.dealer = self.dealer_play()
                    return self.finish_round()

            else:
                # negative reward and immedidate termination of round for invalid action
                self.invalid_action_counter += 1
                return self.finish_invalid_round()

        elif action == 3: # Split
            hand_value = self.current_hand.hand_value()

            if (self.player.split_hand(self.current_hand, self.deck)):
                new_hand = self.update_hand()

                if(new_hand):
                    print("Moving on to new hand")
                    return self.get_obs(), 0, False, False, {}

                else:
                    print("All hands finished")
                    self.dealer = self.dealer_play()
                    return self.finish_round()

            else:
                # negative reward and immedidate termination of round for invalid action
                self.invalid_action_counter += 1
                return self.finish_invalid_round()