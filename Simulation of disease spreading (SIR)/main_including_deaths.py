import numpy as np
from tqdm import tqdm
from Agent import *
from plots import *

# Execution parameters
runs = 3
animate = False
plot_SIR = True

# SIR parameters
alfa = 0.01        # Re-susceptible rate
beta = 0.6      # Infection rate
gamma = 0.025    # Recovery rate
#mu = 0        # Death rate
mu_list = [0] #np.linspace(0, 0.1, 41)
beta_list = [1]#np.linspace(0.03, 1, 21)

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
    n_dead = 0
    for i in list_of_agents:
        current_status = i.status
        if current_status == 0:
            n_susceptible += 1
        elif current_status == 1:
            n_infected += 1
        elif current_status == 2:
            n_recovered += 1
        else:
            n_dead += 1
    return n_susceptible, n_infected, n_recovered, n_dead


def main():
    average_r_inf_list = []
    average_d_inf_list = []
    for i_beta, mu in enumerate(tqdm(mu_list)):
        r_inf = 0
        d_inf = 0
        for run in range(runs):
            list_of_agents = initialize_agents(beta, gamma)
            n_susceptible, n_infected, n_recovered, n_dead = get_all_status(list_of_agents)
            susceptible_list = [n_susceptible]
            infected_list = [n_infected]
            recovered_list = [n_recovered]
            dead_list = [n_dead]

            while n_infected > 0:
            #for t in tqdm(range(2000)):
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
                        r2 = np.random.rand()
                        if r1 < gamma:
                            agent.update_status(status_dict['recovered'])
                        elif r2 < mu:
                            agent.update_status(status_dict['dead'])

                # Re-susceptible
                for agent in list_of_agents:
                    if agent.status == 2:
                        r = np.random.rand()
                        if r < alfa:
                            agent.update_status(status_dict['susceptible'])

                # Get status of all agents
                n_susceptible, n_infected, n_recovered, n_dead = get_all_status(list_of_agents)
                susceptible_list.append(n_susceptible)
                infected_list.append(n_infected)
                recovered_list.append(n_recovered)
                dead_list.append(n_dead)

                if animate:
                    animate_disease_spread(list_of_agents, L)

            r_inf += recovered_list[-1]
            d_inf += dead_list[-1]

            if plot_SIR:
                plot_number_of_agents_vs_SIR(susceptible_list, infected_list, recovered_list, beta, gamma, alfa)

        average_r_inf_list.append(r_inf/runs)
        average_d_inf_list.append(d_inf/runs)
        print(d_inf/runs)

    #np.save('r_inf_array.npy', average_r_inf_list)
    #np.save('r_inf3.npy', average_r_inf_list)
    #np.save(d_inf3.npy', average_d_inf_list)
    plt.scatter(mu_list, average_d_inf_list, color='r', label='dead')
    plt.legend()
    plt.xlabel(r"$\mu$")
    plt.ylabel(f"$D_\infty$")
    plt.show()

if __name__ == '__main__':
    main()