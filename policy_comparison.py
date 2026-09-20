import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from stable_baselines3 import DQN, PPO
import config as cfg


# Create results folder
os.makedirs("results", exist_ok=True)


# =========================
# LOAD TRAINED MODELS
# =========================

dqn_model = DQN.load("models/DQN_blackjack_bot")
ppo_model = PPO.load("models/PPO_blackjack_bot")


# =========================
# ACTIONS
# =========================

ACTION_LETTERS = {
    0: "H",
    1: "S",
    2: "D",
    3: "P"
}


# =========================
# PLAYER HANDS
# =========================

player_totals = list(range(5, 21))

representative_hands = {
    5: [2, 3],
    6: [2, 4],
    7: [2, 5],
    8: [2, 6],
    9: [2, 7],
    10: [2, 8],
    11: [2, 9],
    12: [2, 10],
    13: [3, 10],
    14: [4, 10],
    15: [5, 10],
    16: [6, 10],
    17: [7, 10],
    18: [8, 10],
    19: [9, 10],
    20: [9, 6, 5]
}

dealer_cards = list(range(2, 12))


# =========================
# BUILD OBSERVATION
# =========================

def build_observation(hand_cards, dealer_card):

    cards = hand_cards.copy()

    while len(cards) < 8:
        cards.append(0)

    hand_value = sum(hand_cards)

    soft = 0

    can_double = (
        len(hand_cards) == 2
    )

    can_split = (
        len(hand_cards) == 2
        and hand_cards[0] == hand_cards[1]
    )

    wager = max(
        1,
        int(
            (cfg.wager_constant + 0.005)
            * cfg.ppo_starter_money
        )
    )

    bankroll = cfg.ppo_starter_money
    win_rate = 0
    round_counter = 0

    return np.array(
        cards + [
            hand_value,
            soft,
            dealer_card,
            wager,
            bankroll,
            win_rate,
            round_counter,
            int(can_double),
            int(can_split)
        ],
        dtype=np.float32
    )


# =========================
# DQN POLICY
# =========================

dqn_policy = np.zeros(
    (len(player_totals), len(dealer_cards)),
    dtype=int
)

for row, total in enumerate(player_totals):

    hand_cards = representative_hands[total]

    for col, dealer_card in enumerate(dealer_cards):

        observation = build_observation(
            hand_cards,
            dealer_card
        )

        action, _states = dqn_model.predict(
            observation,
            deterministic=True
        )

        dqn_policy[row, col] = int(action)


# =========================
# PPO POLICY
# =========================

ppo_policy = np.zeros(
    (len(player_totals), len(dealer_cards)),
    dtype=int
)

for row, total in enumerate(player_totals):

    hand_cards = representative_hands[total]

    for col, dealer_card in enumerate(dealer_cards):

        observation = build_observation(
            hand_cards,
            dealer_card
        )

        action, _states = ppo_model.predict(
            observation,
            deterministic=True
        )

        ppo_policy[row, col] = int(action)


# =========================
# RANDOM POLICY
# =========================

np.random.seed(42)

random_policy = np.random.randint(
    0,
    4,
    size=(len(player_totals), len(dealer_cards))
)


# =========================
# PRINT POLICIES
# =========================

def print_policy(name, policy):

    print()
    print("=" * 60)
    print(name)
    print("=" * 60)

    print("      ", end="")

    for dealer_card in dealer_cards:
        if dealer_card == 11:
            print(" A ", end="")
        else:
            print(f"{dealer_card:2} ", end="")

    print()

    for row, total in enumerate(player_totals):

        print(f"{total:2}    ", end="")

        for col in range(len(dealer_cards)):

            print(
                f" {ACTION_LETTERS[policy[row, col]]} ",
                end=""
            )

        print()


print_policy("DQN POLICY", dqn_policy)
print_policy("PPO POLICY", ppo_policy)
print_policy("RANDOM POLICY", random_policy)


# =========================
# CALCULATE AGREEMENT
# =========================

dqn_ppo_agreement = (
    dqn_policy == ppo_policy
).mean() * 100

dqn_random_agreement = (
    dqn_policy == random_policy
).mean() * 100

ppo_random_agreement = (
    ppo_policy == random_policy
).mean() * 100

print()
print("=" * 60)
print("POLICY AGREEMENT")
print("=" * 60)

print(
    f"DQN vs PPO: "
    f"{dqn_ppo_agreement:.2f}%"
)

print(
    f"DQN vs Random: "
    f"{dqn_random_agreement:.2f}%"
)

print(
    f"PPO vs Random: "
    f"{ppo_random_agreement:.2f}%"
)


# =========================
# PLOT
# =========================

fig, axes = plt.subplots(
    1,
    3,
    figsize=(18, 8)
)


# Same scale for every heatmap
cmap = plt.cm.Set2


# -------------------------
# DQN
# -------------------------

axes[0].imshow(
    dqn_policy,
    cmap=cmap,
    vmin=0,
    vmax=3,
    aspect="auto"
)

axes[0].set_title(
    "DQN",
    fontsize=18,
    fontweight="bold"
)


# -------------------------
# PPO
# -------------------------

axes[1].imshow(
    ppo_policy,
    cmap=cmap,
    vmin=0,
    vmax=3,
    aspect="auto"
)

axes[1].set_title(
    "PPO",
    fontsize=18,
    fontweight="bold"
)


# -------------------------
# Random
# -------------------------

axes[2].imshow(
    random_policy,
    cmap=cmap,
    vmin=0,
    vmax=3,
    aspect="auto"
)

axes[2].set_title(
    "Random",
    fontsize=18,
    fontweight="bold"
)


# =========================
# AXES
# =========================

for ax in axes:

    ax.set_xlabel(
        "Dealer Up Card",
        fontsize=12
    )

    ax.set_ylabel(
        "Player Hand Total",
        fontsize=12
    )

    ax.set_xticks(
        range(len(dealer_cards))
    )

    ax.set_xticklabels(
        ["2", "3", "4", "5", "6", "7", "8", "9", "10", "A"]
    )

    ax.set_yticks(
        range(len(player_totals))
    )

    ax.set_yticklabels(
        player_totals
    )


# =========================
# ACTION LETTERS
# =========================

policies = [
    dqn_policy,
    ppo_policy,
    random_policy
]

for ax, policy in zip(axes, policies):

    for row in range(len(player_totals)):

        for col in range(len(dealer_cards)):

            ax.text(
                col,
                row,
                ACTION_LETTERS[
                    policy[row, col]
                ],
                ha="center",
                va="center",
                fontsize=10,
                fontweight="bold"
            )


# =========================
# LEGEND
# =========================

legend_elements = [
    Patch(
        facecolor=cmap(0 / 3),
        label="H = Hit"
    ),
    Patch(
        facecolor=cmap(1 / 3),
        label="S = Stand"
    ),
    Patch(
        facecolor=cmap(2 / 3),
        label="D = Double"
    ),
    Patch(
        facecolor=cmap(3 / 3),
        label="P = Split"
    )
]

fig.legend(
    handles=legend_elements,
    loc="lower center",
    ncol=4,
    frameon=False,
    fontsize=12
)


# =========================
# TITLE
# =========================

fig.suptitle(
    "Learned Blackjack Policies: DQN vs. PPO vs. Random",
    fontsize=22,
    fontweight="bold"
)

plt.tight_layout(
    rect=[0, 0.08, 1, 0.94]
)


# =========================
# SAVE
# =========================

plt.savefig(
    "results/blackjack_policy_comparison.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print()
print("Saved chart to:")
print("results/blackjack_policy_comparison.png")