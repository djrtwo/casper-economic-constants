import argparse

from reward import calculate_annual_interest, calculate_validator_half_life
from reward import EPOCHS_PER_DAY



def calculate_interest_factor(target_annual_interest, initial_deposits, penalty_factor=0.0):
    interest_factor = 0.01
    while True:
        percent_gain = calculate_annual_interest(initial_deposits, 1.0, interest_factor, penalty_factor)

        # return if within +/- 0.1%
        if percent_gain > (target_annual_interest * 0.999) and percent_gain < (target_annual_interest * 1.001):
            return interest_factor

        # change estimate for next round
        if percent_gain > target_annual_interest:
            interest_factor = interest_factor * 0.9
        else:
            interest_factor = interest_factor * 1.1


def calculate_penalty_factor(target_day_half_life, initial_deposits,
                             interest_factor, fraction_offline):
    penalty_factor = 0.0005
    while True:
        epoch_half_life = calculate_validator_half_life(initial_deposits, fraction_offline,
                                                        interest_factor, penalty_factor)

        day_half_life = epoch_half_life / EPOCHS_PER_DAY
        # print("penalty:\t%.6f" % penalty_factor)
        # print("epochs:\t\t%s" % epoch_half_life)
        # print("days:\t\t%.2f" % day_half_life)
        # print("")

        # return if within +/- .1%
        if day_half_life > (target_day_half_life * 0.999) and day_half_life < (target_day_half_life * 1.001):
            return penalty_factor

        # change estimate for next round
        if day_half_life > target_day_half_life:
            penalty_factor = penalty_factor * 1.02
        else:
            penalty_factor = penalty_factor * 0.98


def main():
    parser = argparse.ArgumentParser(description='Run FFG reward script.')
    parser.add_argument(
        'target_interest', type=float,
        help='the target annual interest as a percent'
    )
    parser.add_argument(
        'target_half_life', type=int,
        help='the target half_life of inactive validators in days'
    )
    parser.add_argument(
        '--offline', type=float, default=0.5,
        help='the fraction of validators that go offline for penalty calculation'
    )
    parser.add_argument(
        '--total-deposits', type=float, default=10000000,
        help='the total initial deposits'
    )

    args = parser.parse_args()

    num_validators = 100
    deposit_size = args.total_deposits / num_validators
    initial_deposits = [deposit_size for i in range(num_validators)]  # target 10 million ether
    assert args.total_deposits == sum(initial_deposits)

    target_interest = args.target_interest
    target_half_life = args.target_half_life
    offline = args.offline

    interest_factor = penalty_factor = 0
    for i in range(10):
        interest_factor = calculate_interest_factor(target_interest, initial_deposits, penalty_factor)
        penalty_factor = calculate_penalty_factor(target_half_life, initial_deposits, interest_factor, offline)

        print("interest_factor:\t%f" % interest_factor)
        print("penalty_factor:\t\t%.10f" % penalty_factor)

        percent_gain = calculate_annual_interest(initial_deposits, 1.0, interest_factor, penalty_factor)
        print("gain:\t%f" % percent_gain)

        if percent_gain < target_interest*1.05 and percent_gain > target_interest*0.95:
            break
        elif percent_gain < target_interest:
            penalty_factor *= 0.95
        else:
            penalty_factor *= 1.05

    percent_gain = calculate_annual_interest(initial_deposits, 1.0, interest_factor, penalty_factor)
    half_life_epochs = calculate_validator_half_life(initial_deposits, args.offline, interest_factor, penalty_factor)
    half_life_days = half_life_epochs / EPOCHS_PER_DAY


    print("")
    print("----- OUTPUT -----")
    print("interest_factor:\t%f" % interest_factor)
    print("penalty_factor:\t\t%.10f" % penalty_factor)
    print("")
    print("Target Interest:\t%f" % target_interest)
    print("Actual Interest:\t%f" % percent_gain)
    print("")
    print("Target Halflife:\t%f days" % target_half_life)
    print("Actual Halflife:\t%f days" % half_life_days)


if __name__ == '__main__':
    main()