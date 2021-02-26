import numpy as np
import matplotlib.pyplot as plt


class Bayesian_Model:
    def __init__(self, no_of_gradations=1000):
        # Return evenly spaced numbers over a specified interval (start, stop, no_of_samples)
        self.theta = np.linspace(0, 1, no_of_gradations)
        # Return a new array filled with 1 / each value by length of array = uniform prior
        self.prior = np.ones(len(self.theta)) / len(self.theta)

    def plot_prior(self):
        plt.plot(self.theta, self.prior)
        plt.xlabel('Theta')
        plt.ylabel('Probability of Success')
        plt.grid()
        plt.show()


def calculate_posterior(prior, game_outcome, theta):
    # p(Data|Theta) = Theta ^ success * (1 - Theta) ^ failure
    # where 'likelihood' is p(Data|Theta)
    likelihood = theta ** game_outcome * (1 - theta) ** (1 - game_outcome)
    # p(Data) = Σ ( p(Data|Theta) * Prior) ∀ Delta
    evidence = np.sum(likelihood * prior)
    # new prior = calculated posterior
    prior = likelihood * prior / evidence
    return prior


def prob_of_event(prior, theta):
    success = (prior * theta).sum()
    # print(success)
    return success


if __name__ == '__main__':
    # For simulating test runs
    # Number of language games
    N = input('Enter the number of games')
    N = int(N)
    # True underlying bias of the case marker, assume arbitrary amount between 0 and 1
    true_theta = input('Enter the underlying true bias of the parameter')
    true_theta = float(true_theta)
    # A series of N 1s [successes and 0s [failures]
    game_outcomes = (np.random.rand(N) <= true_theta).astype(int)
    model = Bayesian_Model()
    for outcome in game_outcomes:
        model.prior = calculate_posterior(model.prior, outcome, model.theta)
    model.plot_prior()
    success = prob_of_event(model.prior, model.theta)
    print('this parameter has', success, 'value of approximated success')
