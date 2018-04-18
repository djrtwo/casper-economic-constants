import math
from copy import copy


BASE_ESF = 0
BLOCK_TIME = 14
EPOCH_LENGTH = 50
# 1/14.0 (blocks/second) * 86400 (seconds/day) * 365 (days/year) * 1/50 (epochs/block)
EPOCHS_PER_YEAR = int((86400 * 365) / (BLOCK_TIME * EPOCH_LENGTH))
# 1/14.3 (blocks/second) * 86400 (seconds/day) * 1/50 (epochs/block)
EPOCHS_PER_DAY = int(86400 / (BLOCK_TIME * EPOCH_LENGTH))




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


def calculate_annual_interest(initial_deposits, fraction_vote,
                              base_interest_factor, base_penalty_factor):
    reward_factor = 0
    deposits = copy(initial_deposits)
    for epoch in range(EPOCHS_PER_YEAR):
        num_voted = int(len(deposits) * fraction_vote)
        deposits = collective_reward(deposits, fraction_vote, reward_factor, 2)
        deposits = [reward_vote(deposit, reward_factor) for deposit in deposits[:num_voted]]
        reward_factor = update_reward_factor(
            sum(deposits),
            BASE_ESF,
            base_interest_factor,
            base_penalty_factor
        )
        if epoch % 3 == 0:
            print("%f,%f" % (epoch, sum(deposits)))

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

    # the validators that keep voting
    voting = initial_deposits[:split_index]
    # the validators that go offline
    offline = initial_deposits[split_index:]
    initial_offline_total = sum(offline)

    reward_factor = 0.0
    esf = BASE_ESF
    epoch_count = 0
    # step forward until the validators that went offline have half total deposits
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
        # print(sum(offline))

        epoch_count += 1

    print(sum(voting) / float(sum(voting) + sum(offline)))
    return epoch_count

# calculate_annual_interest([4e6]*10, 1.0, 0.006933, 0.0000002052)
print(calculate_validator_half_life([2.5e5]*10, 0.5, 6.933e-3, 2.052e-7))

