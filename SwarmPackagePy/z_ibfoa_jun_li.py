import numpy as np
from random import random

from . import intelligence


class z_ibfoa_jun_li(intelligence.sw):
    """
    Bacteria Foraging Optimization
    This work is based on the paper published by Jun Li
    "Analysis and Improvement of the Bacterial Foraging Optimization Algorithm"
    Year : 2014
    Author: Jun Li
    Developer: Mahesh Dananjaya
    """

    def cell_to_cell_function(self, agents, i):
        #print('cell-to-cell interactions')

        T = np.array(self.__agents)
        T_diff = (T - T[i])
        T_diff_sq = T_diff**2
        T_sum = np.sum(T_diff_sq, axis=1)
        T_sum_a = (-self.Wa) * T_sum
        T_sum_r = (-self.Wr) * T_sum
        T_sum_a_exp = np.exp(T_sum_a)
        T_sum_r_exp = np.exp(T_sum_r)
        T_sum_aa = -self.Da * T_sum_a_exp
        T_sum_rr = self.Hr * T_sum_r_exp
        J_cc = sum(T_sum_aa) + sum(T_sum_rr)
        #if(i == self.N / 2):
            #print(J_cc)
        return J_cc

    def __init__(self, n, function, lb, ub, dimension, iteration, Nre=16, Ned=4, Nc=2, Ns=12, C=0.1, Ped=0.25, Da=0.1, Wa=0.2, Hr=0.1, Wr=10, lamda=400, L=0.03):
        """
        :param n: number of agents
        :param function: test function
        :param lb: lower limits for plot axes
        :param ub: upper limits for plot axes
        :param dimension: space dimension
        :param iteration: the number of iterations
        :param Nc: number of chemotactic steps (default value is 2)
        :param Ns: swimming length (default value is 12)
        :param C: the size of step taken in the random direction specified by
        the tumble (default value is 0.2)
        :param Ped: elimination-dispersal probability (default value is 1.15)
        """

        super(z_ibfoa_jun_li, self).__init__()
        # Randomly populate the individuals in the intial population
        self.__agents = np.random.uniform(lb, ub, (n, dimension))
        self._points(self.__agents)

        n_is_even = True
        if n & 1:
            n_is_even = False

        self.Da = Da
        self.Wa = Wa
        self.Hr = Hr
        self.Wr = Wr
        self.N = n

        J = np.array([function(x) for x in self.__agents])
        J_fit = np.array([J[x] for x in range(n)])  # [for p in J] #p
        #J_fit = J
        J_cc = np.array([0.0 for x in self.__agents])
        self._points(self.__agents)
        Pbest = self.__agents[J.argmin()]
        Gbest = Pbest
        J_best = function(Gbest)

        C_a = [C for i in range(n)]
        self.__Steps = []
        # self.cell_to_cell_function(self.__agents,1)
        self.__JFitList = []
        self.__JCCList = []
        self.__JARList = []
        self.__JList = []
        self.__JBList = []

        generation = 0
        iteration = 0
        beta = 20 # Q value update frequency
        Ged = 0 # generation MOD 20
        Q  = 1 #percentage of bacteria to be eliniated and disperes


        for l in range(Ned):

            for k in range(Nre):

                J_chem = [J[::1]]
                #BUG J_last = J[::1]
                J_fit = np.array(J)
                J_last = np.array(J)

                for j in range(Nc):

                    for i in range(n):

                        # Can move inside
                        dell = np.random.uniform(-1, 1, dimension)
                        C_a[i] = 1 / (1 + (lamda / np.abs(J[i])))
                        #C_a[i] = 1 / (1 + (lamda / np.abs(J[i]-J_best)))
                        self.__agents[i] += C_a[i] * \
                            np.linalg.norm(dell) * dell

                        J_fit[i] = function(self.__agents[i])
                        J_cc[i] = self.cell_to_cell_function(self.__agents, i)
                        J[i] = J_fit[i] + J_cc[i]

                        if J[i] < J_best:
                            Gbest = self.__agents[i]
                            J_best = J[i]

                       # Monitoring
                        if(i == n / 2):
                            self.__JFitList.append(J_fit[i])
                            self.__JCCList.append(J_cc[i])
                            self.__JList.append(J[i])
                            self.__JBList.append(J_best)
                            self.__Steps.append(C_a[i])
                            #print(C_a[i], J_fit[i], J_cc[i], J[i],(J_fit[i] + J_cc[i]), J_best)
                        # Start Swim Steps
                        for m in range(Ns):

                            # bacteria moves only when objective function is reduced
                            if J[i] < J_last[i]:
                                J_last[i] = J[i]
                                C_a[i] = 1 / (1 + (lamda / np.abs(J[i])))
                                #C_a[i] = 1 / (1 + (lamda / np.abs(J[i]-J_best)))
                                self.__agents[i] += C_a[i] * np.linalg.norm(dell) \
                                    * dell
                                J_fit[i] = function(self.__agents[i])
                                J_cc[i] = self.cell_to_cell_function(
                                    self.__agents, i)
                                J[i] = J_fit[i] + J_cc[i]

                                if J[i] < J_best:
                                    Gbest = self.__agents[i]
                                    J_best = J[i]

                                # Probing
                                if(i == n / 2):
                                    self.__JFitList.append(J_fit[i])
                                    self.__JCCList.append(J_cc[i])
                                    self.__JList.append(J[i])
                                    self.__JBList.append(J_best)
                                    self.__Steps.append(C_a[i])
                                    #print(C_a[i], J_fit[i], J_cc[i],J[i], (J_fit[i] + J_cc[i])), J_best
                                #J[i] = function(self.__agents[i])+ self.cell_to_cell_function(self.__agents, i)
                            else:
                                break

                    self._points(self.__agents)  # Add to the animation
                    # End of Chemotaxis
                    # Make lgorithm faster
                    #J = np.array([function(x) for x in self.__agents])
                    J_chem += [J]
                    generation += 1

                # Ending Chemotaxix Steps of all individuals
                J_chem = np.array(J_chem)

                #J_health = [(sum(J_chem[:, i]), i) for i in range(n)]
                J_health = [(sum(J_chem[:, i]), i, J[i]) for i in range(n)]
                # print(J_health)
                # Sorting: Performance#1
                J_health.sort()
                alived_agents = []
                alived_fits = []
                for i in J_health:
                    alived_agents += [list(self.__agents[i[1]])]
                    alived_fits += [i[2]]

                if n_is_even:
                    alived_agents = 2 * alived_agents[:n // 2]
                    self.__agents = np.array(alived_agents)
                    alived_fits = 2 * alived_fits[:n // 2]
                    J = np.array(alived_fits)

                else:
                    alived_agents = 2 * \
                        alived_agents[:n // 2] + [alived_agents[n // 2]]
                    self.__agents = np.array(alived_agents)
                    alived_fits = 2 * \
                        alived_fits[:n // 2] + [alived_fits[n // 2]]
                    J = np.array(alived_fits)

            if l < Ned - 2:
                """"""
                J_ed = [(J[i],i) for i in range(n)]
                J_ed.sort()
               
                Ged = generation / beta #beta=20
                Q = 1 - (2*Ged*L)
                
                S_ed = Q*n

                if(S_ed<0): 
                    S_ed=0

                sed=int(S_ed)
                print('Elimination and Dispersal')
                print(generation, Ged, Q, S_ed, sed)
                """"""
                for i in range(n-sed,n):
                #for i in range(n):
                    r = random()
                    # if r >= Ped_list[t]:
                    if r >= Ped:

                        self.__agents[J_ed[i][1]] = np.random.uniform(lb, ub, dimension)
                        J[i] = function(self.__agents[i])
                        if J[i] < J_best:
                            Gbest = self.__agents[i]
                            J_best = J[i]

        #END of Process
        print('Best Fitness',J_best)
        print('Solution', Gbest)

        """
        J = np.array([function(x) for x in self.__agents])
        self._points(self.__agents)
        Pbest = self.__agents[J.argmin()]
        if function(Pbest) < function(Gbest):
            Gbest = Pbest
        self._set_Gbest(Gbest)
        """

    def _get_jfits(self):
        return self.__JFitList

    def _get_jcclist(self):
        return self.__JCCList

    def _get_jarlist(self):
        return self.__JARList

    def _get_jlist(self):
        return self.__JList

    def _get_jblist(self):
        return self.__JBList

    def _get_csteps(self):
        return self.__Steps

        #J = np.array([function(x) for x in self.__agents])
        #Pbest = self.__agents[J.argmin()]
        #    if function(Pbest) < function(Gbest):
        #        Gbest = Pbest
        #        J_best = function(Gbest)
