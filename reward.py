import math
from copy import copy


BASE_ESF = 2


def sqrt_of_total_deposits(deposits):
    return math.sqrt(deposits)


def reward_vote(deposit, reward_factor):
    return deposit * (1 + reward_factor)


def collective_reward(deposits, vote_fraction, reward_factor, esf):
    if esf <= 2:
        collective_reward = vote_fraction * reward_factor / 2
    else:
        collective_reward = 0

    return [
        deposit * (1 + collective_reward) / (1 + reward_factor)
        for deposit in deposits
    ]


def update_reward_factor(total_deposits, esf, base_interest_factor, base_penalty_factor):
    return base_interest_factor / sqrt_of_total_deposits(total_deposits) \
           + base_penalty_factor * esf


def calculate_annual_interest(initial_deposits, fraction_vote, base_interest_factor, base_penalty_factor):
    # 1/14.0 (blocks/second) * 86400 (seconds/day) * 365 (days/year) * 1/50 (epochs/block)
    epochs_per_year = (86400 * 365) / (14 * 50)
    reward_factor = 0
    deposits = copy(initial_deposits)
    for epoch in range(epochs_per_year):
        num_voted = int(len(deposits) * fraction_vote)
        deposits = collective_reward(deposits, fraction_vote, reward_factor, 2)
        deposits = [reward_vote(deposit, reward_factor) for deposit in deposits[:num_voted]]
        reward_factor = update_reward_factor(
            sum(deposits),
            BASE_ESF,
            base_interest_factor,
            base_penalty_factor
        )

    initial_total = sum(initial_deposits)
    end_total = sum(deposits)
    issuance = end_total - initial_total
    interest = issuance / initial_total
    percent_gain = interest * 100

    print("interest_factor:\t%f" % base_interest_factor)
    print("initial:\t\t%s" % initial_total)
    print("end:\t\t\t%s" % end_total)
    print("issuance:\t\t%s" % issuance)
    print("interest:\t\t%.2f%%" % percent_gain)
    print("")

    return percent_gain


def calculate_validator_half_life(initial_deposits, fraction_offline,
                                  base_interest_factor, base_penalty_factor):
    split_index = int(len(initial_deposits) * (1 - fraction_offline))
    voting = initial_deposits[:split_index]
    offline = initial_deposits[split_index:]
    initial_offline_total = sum(offline)
    reward_factor = 0.0
    esf = BASE_ESF
    epoch_count = 0
    while sum(offline) > 0.5 * initial_offline_total:
        fraction_voted = sum(voting) / float((sum(voting + offline)))
        voting = collective_reward(voting, fraction_voted, reward_factor, esf)
        offline = collective_reward(offline, fraction_voted, reward_factor, esf)
        voting = [reward_vote(deposit, reward_factor) for deposit in voting]

        if fraction_voted >= 2/3.0:
            esf = BASE_ESF
        else:
            esf += 1

        reward_factor = update_reward_factor(
            sum(voting + offline),
            esf,
            base_interest_factor,
            base_penalty_factor
        )

        epoch_count += 1

    return epoch_count
