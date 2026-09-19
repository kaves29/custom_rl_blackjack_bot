import random
from dataclasses import dataclass

@dataclass
class Card:
    suit: str
    rank: str
    value: int

class Deck:
    def __init__(self, deck, num_decks):
        self.deck = deck
        self.num_decks = num_decks # added for the future

    def create(self):
        """Creates new deck"""

        if len(self.deck) != 0:
            print("DEBUG: THE DECK IS ALREADY GENERATED!")

        suits = ["Spades", "Hearts", "Diamonds", "Clubs"]
        for suit in suits:
            for num_card in range(2, 11):
                self.deck.append(
                    Card(suit=suit, rank=str(num_card), value=num_card)
                )
            for face_card in ["J", "Q", "K", "A"]:
                self.deck.append(
                    Card(suit=suit, rank=face_card, value=10 if face_card != "A" else 11) # base case of 11 for an Ace 
                )

        return random.shuffle(self.deck)

    def deal(self, num_cards):
        """Draws num_cards number of cards"""

        drawn_cards = []
        for _ in range(num_cards):
            card_drawn = self.deck.pop()
            drawn_cards.append(card_drawn)

        return drawn_cards
    
    def draw(self):
        """Draws one card"""
        return self.deck.pop()

class Hand:
    def __init__(self, cards, wager):
        self.cards = cards
        self.wager = wager
        self.soft = None
        self.bust = None
        self.blackjack = None
        self.doubled = False
        self.finished = False
        self.was_split = False

    def hand_value(self):
        curr_value = sum(card.value for card in self.cards)
        num_aces = sum(card.rank == "A" for card in self.cards)

        aces_remaining = num_aces
        while curr_value > 21 and aces_remaining > 0:
            curr_value -= 10
            aces_remaining -= 1

        self.bust = curr_value > 21
        self.soft = (aces_remaining > 0) and not self.bust
        self.blackjack = (
            curr_value == 21
            and len(self.cards) == 2
            and not self.was_split
        )

        return curr_value

    def is_pair(self):
        if (len(self.cards) == 2) and (self.cards[0].rank == self.cards[1].rank):
            return True
        else:
            return False


class Player:
    def __init__(self, player_money):
        self.player_money = player_money
        self.hands = []

    def initial_bet(self, player_bet):
        while (player_bet > self.player_money) or (player_bet <= 0):
            player_bet = int(input("Please place a valid bet amount: "))
        self.player_money -= player_bet
        hand = Hand([], player_bet)
        self.hands.append(hand)

    def double_hand(self, hand, deck):
        if (not hand.doubled) and (len(hand.cards) == 2) and (hand.wager <= self.player_money) and not hand.blackjack and not hand.bust:
            self.player_money -= hand.wager
            hand.wager += hand.wager
            hand.doubled = True
            hand.cards.append(deck.draw())
            hand.hand_value()
            hand.finished = True

            return True
        
        return False

    def split_hand(self, hand, deck):
        if (hand.is_pair() and not hand.finished and not hand.was_split and self.player_money >= hand.wager):
            hand_1_cards = [hand.cards[0], deck.draw()]
            hand_2_cards = [hand.cards[1], deck.draw()]
            new_hand_1 = Hand(hand_1_cards, hand.wager)
            new_hand_2 = Hand(hand_2_cards, hand.wager)
            new_hand_1.was_split = True
            new_hand_2.was_split = True
            self.player_money -= hand.wager

            hand_index = self.hands.index(hand)
            self.hands[hand_index] = new_hand_1
            self.hands.insert(hand_index + 1, new_hand_2)
            new_hand_1.hand_value()
            new_hand_2.hand_value()

            return True

        return False