import numpy as np
from random import random
import random
from . import intelligence
import os
import time
from memory_profiler import profile
import psutil

class z_bfoa_general_v1_max(intelligence.sw):
    """
    With both discrete and continous domains
    Also, UP and LB can be limited


    Bacteria Foraging Optimization
    This work is based on the paper published by Jun Li
    "Analysis and Improvement of the Bacterial Foraging Optimization Algorithm"
    Year : 2014
    Author: Jun Li
    Developer: Mahesh Dananjaya

    All included
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
        self.evaluations = self.evaluations +1
        # if(i == self.N / 2):
        # print(J_cc)
        return J_cc

    def __init__(self, n, function, lb, ub, dimension, iteration, Nre=16, Ned=4, Nc=2, Ns=12, C=0.1, Ped=0.25, Da=0.1, Wa=0.2, Hr=0.1, Wr=10, lamda=400, L=0.03, arga='none', argj='none', arged='false',search_type='continuous', search_strategy='min'):
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
        
        search_type : Discrete or Continuous
        """

        super(z_bfoa_general_v1_max, self).__init__()

        print(n, function, lb, ub, dimension, iteration, Nre, Ned, Nc,
              Ns, C, Ped, Da, Wa, Hr, Wr, lamda, L, arga, argj, arged)
        # Randomly populate the individuals in the intial population

        #Process
        process = psutil.Process(os.getpid())

        #decision for Discrete or Continous Optimization
        if(search_type == 'continuous'):
            print('Continous Domain')
            r = random.choice([(lb[i],ub[i]) for i in range(dimension)])
            #self.__agents = np.random.uniform(lb, ub, (n, dimension))
            self.__agents = np.random.uniform(*r, (n, dimension))
        elif(search_type == 'discrete'):
            print('Discrete Domain')
            r = random.choice([(lb[i],ub[i]) for i in range(dimension)])
            self.__agents = np.random.random_integers(*r, (n, dimension))
        else:
            print('Neither Discrete or Continous: Combinatorial?')
            return

        #Sample Points    
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
        J_ar = np.array([0.0 for x in self.__agents])
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
        beta = 20  # Q value update frequency
        Ged = 0  # generation MOD 20
        Q = 1  # percentage of bacteria to be eliniated and disperes

        self.evaluations = 0
        self.gbesteval = 0

        #process = psutil.Process(os.getpid())
        start_time = time.time()   

        for l in range(Ned):

            for k in range(Nre):

                J_chem = [J[::1]]
                #J_last = J[::1] #BUG
                J_last = np.array(J)

                J_fit = np.array(J)

                for j in range(Nc):

                    for i in range(n):

                        # Can move inside
                        if(search_type == 'continuous'):
                            dell = np.random.uniform(-1, 1, dimension)
                        elif(search_type == 'discrete'):
                            dell = np.random.random_integers(-1, 1, dimension)
                        else:
                            print('Error: No Search Type Defined')
                            return

                        #####################################################
                        if(arga == 'adaptive1'):
                            C_a[i] = 1 / (1 + (lamda / np.abs(J[i])))
                        elif(arga == 'adaptive2'):
                            C_a[i] = 1 / (1 + (lamda / np.abs(J[i] - J_best)))
                        elif(arga == 'improved1'):
                            C_a[i] = C_a[i] / (2 * (generation // 10))
                        else:
                            C_a[i] = C_a[i]  # Doing nothing
                        #####################################################

                        #Discrimination Between Discrete and Continuous
                        if(search_type == 'continuous'):
                            self.__agents[i] += C_a[i] * np.linalg.norm(dell) * dell
                        elif(search_type == 'discrete'):
                            self.__agents[i] += dell
                            #Should COnsider LImiting Vlaues: Overflow
                        else:
                            print('Error:No Search Type Defined')
                            return

                        J_fit[i] = function(self.__agents[i])
                        J_cc[i] = self.cell_to_cell_function(self.__agents, i)

                        if(search_strategy == 'max'):
                            J_cc[i] = J_cc[i]*-1

                        #####################################################

                        #print('ERROR1', J[i], J_last[i])

                        if(argj == 'swarm1'):
                            J[i] = J_fit[i] + J_cc[i]
                        elif (argj == 'swarm2'):
                            J_ar[i] = np.exp(-J_fit[i]) * J_cc[i]
                            J[i] = J_fit[i] + J_ar[i]
                        else:
                            J[i] = J_fit[i]

                        #print('ERROR2', J[i], J_last[i])
                        #####################################################
                        if(search_strategy == 'min'):
                            if J[i] < J_best:
                                Gbest = self.__agents[i]
                                J_best = J[i]
                                self.gbesteval = self.evaluations
                        elif(search_strategy == 'max'):
                            if J[i] > J_best:
                                Gbest = self.__agents[i]
                                J_best = J[i]
                                self.gbesteval = self.evaluations
                        else:
                            print('Undefined Search Strategy')
                        ######################################################
                       # Monitoring #probe Point n/2
                        if(i == n / 2):
                            self.__JFitList.append(J_fit[i])
                            self.__JCCList.append(J_cc[i])
                            self.__JARList.append(J_ar[i])
                            self.__JList.append(J[i])
                            self.__JBList.append(J_best)
                            self.__Steps.append(C_a[i])
                            #print(C_a[i], J_fit[i], J_cc[i], J[i],(J_fit[i] + J_cc[i]), J_best)
                        #####################################################
                        # Start Swim Steps
                        #print('Here')
                        for m in range(Ns):
                            #print('Print', l,k,j,i,m)
                            #if(m == (Ns - 1)):
                            #    print('HitMax', generation)

                            # bacteria moves only when objective function is reduced
                            #print('BEST', J[i], J_last[i])
                            #if (( search_strategy == 'min' and (J[i] < J_last[i])) or ( search_strategy == 'max' and (J[i] > J_last[i])) ):
                            if (( search_strategy == 'min' and (J[i] <= J_last[i])) or ( search_strategy == 'max' and (J[i] >= J_last[i])) ):
                                J_last[i] = J[i]

                                ##############################################################
                                if(arga == 'adaptive1'):
                                    C_a[i] = 1 / (1 + (lamda / np.abs(J[i])))
                                elif(arga == 'adaptive2'):
                                    C_a[i] = 1 / \
                                        (1 + (lamda / np.abs(J[i] - J_best)))
                                elif(arga == 'improved1'):
                                    C_a[i] = C_a[i] / (2 * (generation // 10))
                                else:
                                    C_a[i] = C_a[i]  # Doing nothing
                            

                                if(search_type == 'continuous'):
                                    self.__agents[i] += C_a[i] * np.linalg.norm(dell) * dell
                                elif(search_type == 'discrete'):
                                    self.__agents[i] += dell
                                else:
                                    print('Error:No Search Type Defined')
                                    return    

                                J_fit[i] = function(self.__agents[i])
                                J_cc[i] = self.cell_to_cell_function(
                                    self.__agents, i)

                                if(search_strategy == 'max'):
                                    J_cc[i] = J_cc[i]*-1

                                #####################################################
                                if(argj == 'swarm1'):
                                    J[i] = J_fit[i] + J_cc[i]
                                elif (argj == 'swarm2'):
                                    J_ar[i] = np.exp(-J_fit[i]) * J_cc[i]
                                    J[i] = J_fit[i] + J_ar[i]
                                else:
                                    J[i] = J_fit[i]
                                #####################################################

                                #J[i] = J_fit[i] + J_cc[i]

                                if ((search_strategy == 'min' and (J[i] < J_best)) or (search_strategy == 'max' and (J[i] > J_best))):
                                    Gbest = self.__agents[i]
                                    J_best = J[i]
                                    self.gbesteval = self.evaluations

                                # Probing
                                if(i == n / 2):
                                    self.__JFitList.append(J_fit[i])
                                    self.__JCCList.append(J_cc[i])
                                    self.__JARList.append(J_ar[i])
                                    self.__JList.append(J[i])
                                    self.__JBList.append(J_best)
                                    self.__Steps.append(C_a[i])
                                    #print('m is of bac ', m)
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

                if(search_strategy == 'max'):
                    J_health.reverse()

                alived_agents = []
                alived_fits = []
                for i in J_health:
                    alived_agents += [list(self.__agents[i[1]])]
                    alived_fits += [i[2]]

                # TMP
                """
                """
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
                """
                """
                # TMP

            if l < Ned - 2:
                """"""
                J_ed = [(J[i], i) for i in range(n)]
                J_ed.sort()

                Ged = generation / beta  # beta=20
                Q = 1 - (0.5 * Ged * L)

                S_ed = Q * n

                if(S_ed < 0):
                    S_ed = 0

                sed = int(S_ed)
                print('Elimination and Dispersal')
                print(generation, Ged, Q, S_ed, sed)
                """"""
                s = 0
                if(arged == 'true'):
                    s = n - sed
                else:
                    s = 0

                for i in range(s, n):
                    # for i in range(n):
                    #r = random()
                    r = np.random.uniform(0, 1, 1)
                    # if r >= Ped_list[t]:
                    if r >= Ped:
                        if(arged == 'true'):
                            self.__agents[J_ed[i][1]] = np.random.uniform(lb, ub, dimension)
                        else:
                            #Discrete Vs Continous
                            if(search_type == 'continuous'):
                                r = random.choice([(lb[i],ub[i]) for i in range(dimension)])
                                #self.__agents[i] = np.random.uniform(lb, ub, dimension)
                                self.__agents[i] = np.random.uniform(*r, dimension)
                            elif(search_type == 'discrete'):
                                r = random.choice([(lb[i],ub[i]) for i in range(dimension)])
                                #self.__agents[i] = np.random.uniform(lb, ub, dimension)
                                self.__agents[i] = np.random.uniform(*r, dimension)

                        J[i] = function(self.__agents[i])
                        J_fit[i] = function(self.__agents[i])
                        #if J[i] < J_best:
                        if ((search_strategy == 'min' and (J[i] < J_best)) or (search_strategy == 'max' and (J[i] > J_best))):

                            Gbest = self.__agents[i]
                            J_best = J[i]
                            self.gbesteval = self.evaluations

        #Memory Isage
        end_time = time.time()
        print('Processing Time')
        print("--- %s seconds ---" % (time.time() - start_time))

        print('######################## Memeory Usage ########################')
        #print(process.memory_info().rss)
        mem_usage = process.memory_info().rss
        #For python 2.7 #print(process.get_memory_info()[0])
        print(mem_usage)
        print("Memory in MB :", mem_usage/float(2**20))       

        
        # END of BFOA
        print('###################Iterative Measurements#######################')
        print('Best Fitness', J_best)
        print('Best FIT Fitness', function(Gbest))
        print('Solution', Gbest)
        print('GBestEval',self.gbesteval)


        #Pbest = self.__agents[J.argmin()]
        print('###################Final Measurements#######################')
        Pbest = self.__agents[J.argmax()]
        Gbest = Pbest
        J_best = function(Gbest)

        print('Best Fitness', J_best)
        print('Solution', Gbest)
        print('Searched J Value',J[J.argmax()])
        print('Searched JFit Value',J_fit[J.argmax()])

        #Pbest_fit = self.__agents[J_fit.argmin()]
        print('###################Original Measurements#######################')
        Pbest_fit = self.__agents[J_fit.argmax()]
        Gbest_fit = Pbest_fit
        J_best_fit = function(Gbest_fit)

        print('Best Fitness', J_best_fit)
        print('Solution', Gbest_fit)

        print('###################Average Measurements#######################')
        print('Average J', sum(J)/n)
        print('Average J_FIT', sum(J_fit)/n)

        print('Average Position', sum(self.__agents)/n)
        agent_a = sum(self.__agents)/n
        Jtmp = function(agent_a)
        print('Fitness with Average Position',Jtmp)

        #print(J_fit[])

        #print('GBestEval',self.gbesteval)
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
