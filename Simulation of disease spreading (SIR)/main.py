import numpy as np
from tqdm import tqdm
from Agent import *
from plots import *

# Execution parameters
runs = 3
animate = True
plot_SIR = False

# SIR parameters
#beta = 0.6      # Infection rate
#gamma = 0.01    # Recovery rate
beta_list = np.linspace(0.1, 1, 21)

# Arena parameters
N = 1000       # number of agents
L = 100        # Arena size
d = 0.8        # Diffusion rate
initial_infected_rate = 0.01
lattice = np.array([L, L]).astype(int)
status_dict = {'susceptible': 0, 'infected': 1, 'recovered': 2, 'dead': 3}


def initialize_agents(beta, gamma):
    list_of_agents = [None] * N
    for i in range(N):
        x = np.random.randint(L)
        y = np.random.randint(L)
        if i < initial_infected_rate * N:
            status = 'infected'
        else:
            status = 'susceptible'
        list_of_agents[i] = Agent(x, y, lattice, beta, gamma, d, status_dict[status])
    return list_of_agents


def get_all_status(list_of_agents):
    n_susceptible = 0
    n_infected = 0
    n_recovered = 0
    for i in list_of_agents:
        current_status = i.status
        if current_status == 0:
            n_susceptible += 1
        elif current_status == 1:
            n_infected += 1
        else:    # current_status == 2:
            n_recovered += 1
    return n_susceptible, n_infected, n_recovered


def main():
    average_r_inf_list = np.zeros((21, 21))
    for i_beta, beta in enumerate(tqdm(beta_list)):
        gamma_list = np.linspace(beta, beta/80, 21)
        for i_gamma, gamma in enumerate(tqdm(gamma_list)):
            r_inf = 0
            for run in range(runs):
                list_of_agents = initialize_agents(beta, gamma)
                n_susceptible, n_infected, n_recovered = get_all_status(list_of_agents)
                susceptible_list = [n_susceptible]
                infected_list = [n_infected]
                recovered_list = [n_recovered]

                while n_infected > 0:
                    # Movement
                    for agent in list_of_agents:
                        if agent.status == 0 or agent.status == 1:
                            agent.move()

                    # Infection
                    for i, agent in enumerate(list_of_agents):
                        if agent.status == 1:
                            for j, uninfected_agent in enumerate(list_of_agents):
                                if uninfected_agent.status == 0 and agent.x == uninfected_agent.x and agent.y == uninfected_agent.y:
                                    r = np.random.rand()
                                    if r < beta:
                                        uninfected_agent.update_status(status_dict['infected'])

                    # Recovery
                    for agent in list_of_agents:
                        if agent.status == 1:
                            r1 = np.random.rand()
                            if r1 < gamma:
                                agent.update_status(status_dict['recovered'])

                    # Get status of all agents
                    n_susceptible, n_infected, n_recovered = get_all_status(list_of_agents)
                    susceptible_list.append(n_susceptible)
                    infected_list.append(n_infected)
                    recovered_list.append(n_recovered)

                    if animate:
                        animate_disease_spread(list_of_agents, L)

                r_inf += recovered_list[-1]
                #d_inf += dead_list[-1]

                if plot_SIR:
                    plot_number_of_agents_vs_SIR(susceptible_list, infected_list, recovered_list, beta, gamma)

            average_r_inf_list[i_beta, i_gamma] = r_inf/runs
            print(r_inf/runs)
    print(np.shape(average_r_inf_list))
    np.save('r_inf_array.npy', average_r_inf_list)

if __name__ == '__main__':
    main()
