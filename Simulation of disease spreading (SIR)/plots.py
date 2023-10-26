import numpy as np
import matplotlib.pyplot as plt


def plot_r_inf():
    r_inf1 = np.load('r_inf.npy')
    r_inf2 = np.load('r_inf2.npy')
    beta_list1 = np.linspace(0, 1, 21) / 0.01
    beta_list2 = np.linspace(0, 1, 21) / 0.02
    plt.scatter(beta_list1, r_inf1, color='r', label='gamma = 0.01')
    plt.scatter(beta_list2, r_inf2, color='g', label='gamma = 0.02')
    plt.legend()
    plt.xlabel(r"$\beta$ / $\gamma$")
    plt.ylabel(f"$R_\infty$")
    plt.show()


def plot_d_inf():
    d_inf = np.load('d_inf')
    mu_list = np.linspace(0, 0.04, 41)
    plt.scatter(mu_list, d_inf, color='r', label='dead')
    plt.legend()
    plt.xlabel(r"$\mu$")
    plt.ylabel(f"$D_\infty$")
    plt.show()


def animate_disease_spread(list_of_agents, L):
    x_list = []
    y_list = []
    color_list = []
    for agent in list_of_agents:
        x_list.append(agent.x)
        y_list.append(agent.y)
        if agent.status == 0:
            color_list.append('r')
        elif agent.status == 1:
            color_list.append('g')
        else:
            color_list.append('b')
    plt.scatter(x_list, y_list, c=color_list)
    plt.xlim([0, L])
    plt.ylim([0, L])
    plt.show()


def plot_number_of_agents_vs_SIR(susceptible_list, infected_list, recovered_list, beta, gamma, alfa):
    plt.plot(susceptible_list, color='r', label='susceptible')
    plt.plot(infected_list, color='g', label='infected')
    plt.plot(recovered_list, color='b', label='recovered')
    plt.legend()
    plt.xlabel('time steps')
    plt.ylabel('number of agents')
    plt.title(f'SIR simulation for beta: {beta}, gamma: {gamma} and alpha: {alfa}')
    plt.show()