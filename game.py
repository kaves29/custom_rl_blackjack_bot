

from engine.hand import Deck, Hand, Player
import random

# Basic terminal UI
def show_hand(name, hand, hide_second_card=False):
    cards = ""
    for i, card in enumerate(hand.cards):
        if hide_second_card and i == 1:
            cards += "[??] "
        else:
            cards += f"[{card.rank}{card.suit[0]}] "

    print(f"{name}: {cards}")
    if not hide_second_card:
        print(f"Total: {hand.hand_value()}")


def show_player_hands(player):
    print("\n" + "=" * 45)
    for i, hand in enumerate(player.hands):
        print(f"Hand {i + 1}: ", end="")
        for card in hand.cards:
            print(f"[{card.rank}{card.suit[0]}]", end=" ")
        print(f"| Total: {hand.hand_value()} | Wager: ${hand.wager}")
        if hand.bust:
            print("-> BUST")
        elif hand.finished:
            print("-> FINISHED")
    print("=" * 45)


print("=" * 45)
print("             BLACKJACK")
print("=" * 45)

num_rounds = int(input("How many rounds do you want to play? "))
# Creating player
player = Player(100)

for round_num in range(num_rounds):

    player.hands = [] # reset of player hands

    # Round setup
    deck = Deck([], 1)
    deck.create()

    print(f"Bankroll: ${player.player_money}")
    initial_player_bet = int(input("Place the amount you want to bet: "))
    player.initial_bet(initial_player_bet)
    # Dealing cards
    player_cards = player.hands[0]
    player_cards.cards.extend(deck.deal(2))

    dealer_cards = Hand(deck.deal(2), 0)
    player_cards.hand_value()
    dealer_cards.hand_value()

    print("\nInitial deal:")
    show_player_hands(player)
    show_hand("Dealer", dealer_cards, True)

    # Checking blackjack
    is_blackjack = True if player_cards.hand_value() == 21 else False
    dealer_blackjack = True if dealer_cards.hand_value() == 21 else False
    if is_blackjack:
        if dealer_blackjack:
            print("\nBoth have blackjack. Tie!")
            player.player_money += player_cards.wager
        else:
            print("\nBLACKJACK! Player wins!")
            player.player_money += player_cards.wager * 2.5

    else:
        if dealer_blackjack:
            print("\nDealer has blackjack!")
        else:
            current_hand_index = 0
            while current_hand_index < len(player.hands):
                player_cards = player.hands[current_hand_index]
                if player_cards.finished:
                    current_hand_index += 1
                    continue

                player_cards.hand_value()
                while not player_cards.finished:
                    print("\n" + "-" * 45)
                    print(f"Playing Hand {current_hand_index + 1}")
                    show_hand("Your hand", player_cards)
                    print(f"Bankroll: ${player.player_money}")
                    print("H = Hit | S = Stand | D = Double | P = Split")

                    decision = input("Choose an action: ").strip().upper()
                    if decision == "H":
                        player_cards.cards.append(deck.draw())

                        print(f"You drew a {player_cards.cards[-1].rank}{player_cards.cards[-1].suit[0]}.")
                        print(f"You are at {player_cards.hand_value()}")
                        if player_cards.bust:
                            print("You busted!")
                            player_cards.finished = True

                        elif player_cards.hand_value() == 21:
                            print("You reached 21!")
                            player_cards.finished = True

                        else:
                            print("You did not bust yet!")

                    elif decision == "S":
                        player_cards.finished = True
                        print("You stand.")

                    elif decision == "D":
                        if player.double_hand(player_cards, deck):
                            print("You doubled!")
                            print(f"You are at {player_cards.hand_value()}")
                            if player_cards.bust:
                                print("You busted!")
                            else:
                                print("Your turn is done.")
                        else:
                            print("You cannot double this hand.")

                    elif decision == "P":
                        if player.split_hand(player_cards, deck):
                            print("You split your hand.")
                            show_player_hands(player)

                        else:
                            print("You cannot split this hand.")

                    else:
                        print("Please enter H, S, D, or P.")
                current_hand_index += 1

    # Dealer's turn
    any_live_hand = False
    for hand in player.hands:
        if not hand.bust:
            any_live_hand = True
            break

    if any_live_hand and not dealer_blackjack:
        print("\nDealer's turn.")
        while (dealer_cards.hand_value() < 17):
            dealer_cards.cards.append(deck.draw())

            print("Dealer drew a card!")
            print(f"Dealer is at {dealer_cards.hand_value()}")
            if dealer_cards.bust:
                print("Dealer busted!")
                break
            else:
                print("Dealer did not bust yet!")

    # Dealer cards reveal
    print("\n" + "=" * 45)
    show_hand("Dealer", dealer_cards)
    print("=" * 45)

    # Result
    if not is_blackjack and not dealer_blackjack:
        for i, player_cards in enumerate(player.hands):
            player_cards.hand_value()
            dealer_cards.hand_value()

            if player_cards.bust:
                print(f"Hand {i + 1}: Dealer won!")

            elif dealer_cards.bust:
                player.player_money += player_cards.wager * 2
                print(f"Hand {i + 1}: Player won!")

            elif player_cards.hand_value() > dealer_cards.hand_value():
                player.player_money += player_cards.wager * 2
                print(f"Hand {i + 1}: Player won!")

            elif player_cards.hand_value() < dealer_cards.hand_value():
                print(f"Hand {i + 1}: Dealer won!")

            else:
                player.player_money += player_cards.wager
                print(f"Hand {i + 1}: Tie!")

    elif not is_blackjack and dealer_blackjack:
        print("Dealer won!")

    print("\n" + "=" * 45)
    print(f"Round over. Final bankroll: ${player.player_money}")
    print("=" * 45)

    if player.player_money == 0:
        break