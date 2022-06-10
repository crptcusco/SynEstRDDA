from satispy import Variable
from satispy.solver import Minisat
from igraph import *  # library to make network graphs
import matplotlib.pyplot as plt  # library to make draws
# import ray # Library to paralelization, distribution and scalability

class RddaModel:
    def __init__(self, number_of_rdda, list_of_v_intern, list_of_signals=[]):
        self.number_of_rdda = number_of_rdda
        self.list_of_v_intern = list_of_v_intern
        self.list_of_signals = list_of_signals
        self.description_variables = []
        self.list_of_v_exterm = []
        self.list_of_v_total = []
        self.dic_var_cnf = {}
        self.number_of_v_intern = 0
        self.number_of_v_extern = 0
        self.number_of_v_total = 0
        self.set_of_attractors = None
        self.dic_res_var = {}
        self.list_permutations_attractors = []

    def proccesParameters(self):

        # Procesesing the input of rdda
        for v_signal in self.list_of_signals:
            # print (v_signal.name_variable)
            self.list_of_v_exterm.append(v_signal.name_variable)
        # update the value of list_variables
        self.list_of_v_total.extend(self.list_of_v_intern.copy())
        self.list_of_v_total.extend(self.list_of_v_exterm.copy())
        self.number_of_v_total = len(self.list_of_v_total)

        # oRdda.show()
        # print(self.list_of_v_total)
        # print(self.list_of_v_exterm)

    def show(self):
        print("================================================================")
        print("RDDA DESCRIPTION")
        print("Name of RDDA : " + str(self.number_of_rdda))
        print("List of intern variables : ")
        print(self.list_of_v_intern)
        print("List of coupling signals : ")
        for signal in self.list_of_signals:
            print("---------------")
            signal.show()
            print("---------------")
        print("Description of Variables")
        for v_description in self.description_variables:
            v_description.show()
        print("================================================================")

    def show_permutation_attractors(self):
        for permutation_attractor in self.list_permutations_attractors:
            print("Permutation: ", permutation_attractor[0], "Attractors: ")
            print(permutation_attractor[1])

    def generate_boolean_formulation(self, number_of_transitions, l_atractors_clausules, permutation):
        # create dictionary of cnf variables!!
        for variable in self.list_of_v_total:
            for transition_c in range(0, number_of_transitions):
                self.dic_var_cnf[str(variable) + "_" + str(transition_c)] = Variable(
                    str(variable) + "_" + str(transition_c))

        # transition_aux = 0
        cont_transition = 0
        boolean_function = Variable("0_0")
        for transition in range(1, number_of_transitions):
            # transition_aux = transition
            cont_clause_global = 0
            boolean_expression_equivalence = Variable("0_0")
            for oVariableModel in self.description_variables:
                cont_clause = 0
                boolean_expression_clause_global = Variable("0_0")
                for clause in oVariableModel.cnf_function:
                    boolean_expression_clause = Variable("0_0")
                    cont_termino = 0
                    for termino in clause:
                        termino_aux = abs(int(termino))
                        if (cont_termino == 0):
                            if (str(termino)[0] != "-"):
                                boolean_expression_clause = self.dic_var_cnf[
                                    str(termino_aux) + "_" + str(transition - 1)]
                            else:
                                boolean_expression_clause = -self.dic_var_cnf[
                                    str(termino_aux) + "_" + str(transition - 1)]
                        else:
                            if (str(termino)[0] != "-"):
                                boolean_expression_clause = self.dic_var_cnf[str(termino_aux) + "_" + str(
                                    transition - 1)] | boolean_expression_clause
                            else:
                                boolean_expression_clause = -self.dic_var_cnf[
                                    str(termino_aux) + "_" + str(transition - 1)] | boolean_expression_clause
                        cont_termino = cont_termino + 1
                    if (cont_clause) == 0:
                        boolean_expression_clause_global = boolean_expression_clause
                    else:
                        boolean_expression_clause_global = boolean_expression_clause_global & boolean_expression_clause
                    cont_clause = cont_clause + 1
                if cont_clause_global == 0:
                    boolean_expression_equivalence = self.dic_var_cnf[str(oVariableModel.name_variable) + "_" + str(
                        transition)] >> boolean_expression_clause_global
                    boolean_expression_equivalence = boolean_expression_equivalence & (
                            boolean_expression_clause_global >> self.dic_var_cnf[
                        str(oVariableModel.name_variable) + "_" + str(transition)])
                else:
                    boolean_expression_equivalence = boolean_expression_equivalence & (self.dic_var_cnf[
                                                                                           str(oVariableModel.name_variable) + "_" + str(
                                                                                               transition)] >> boolean_expression_clause_global)
                    boolean_expression_equivalence = boolean_expression_equivalence & (
                            boolean_expression_clause_global >> self.dic_var_cnf[
                        str(oVariableModel.name_variable) + "_" + str(transition)])
                if oVariableModel.cnf_function == []:
                    print("ATYPICAL CASE")
                    boolean_function = boolean_function & (
                            self.dic_var_cnf[str(oVariableModel.name_variable) + "_" + str(transition)] | -
                    self.dic_var_cnf[str(oVariableModel.name_variable) + "_" + str(transition)])
                cont_clause_global = cont_clause_global + 1
            if cont_transition == 0:
                boolean_function = boolean_expression_equivalence
            else:
                boolean_function = boolean_function & boolean_expression_equivalence
            # VALIDAR LOS GENES EN BLANCO
            cont_transition = cont_transition + 1

        # ASSING VALUES FOR PERMUTATIONS
        cont_permutacion = 0
        for elemento in self.list_of_v_exterm:
            # print oRDD.list_of_v_exterm
            for v_transition in range(0, number_of_transitions):
                # print l_signal_coupling[cont_permutacion]
                if permutation[cont_permutacion] == "0":
                    boolean_function = boolean_function & -self.dic_var_cnf[str(elemento) + "_" + str(v_transition)]
                    # print (str(elemento) +"_"+ str(v_transition))
                else:
                    boolean_function = boolean_function & self.dic_var_cnf[str(elemento) + "_" + str(v_transition)]
                    # print (str(elemento) +"_"+ str(v_transition))
            cont_permutacion = cont_permutacion + 1

        # add atractors to boolean function
        if len(l_atractors_clausules) > 0:
            boolean_function_of_attractors = Variable("0_0")
            cont_clause = 0
            for clause in l_atractors_clausules:
                boolean_expression_clause_of_attractors = Variable("0_0")
                cont_termino = 0
                for termino in clause:
                    termino_aux = abs(int(termino))
                    # print str(termino_aux) + "_" + str(number_of_transitions-1)
                    if cont_termino == 0:
                        if termino[0] != "-":
                            boolean_expression_clause_of_attractors = self.dic_var_cnf[
                                str(termino_aux) + "_" + str(number_of_transitions - 1)]
                        else:
                            boolean_expression_clause_of_attractors = -self.dic_var_cnf[
                                str(termino_aux) + "_" + str(number_of_transitions - 1)]
                    else:
                        if termino[0] != "-":
                            boolean_expression_clause_of_attractors = boolean_expression_clause_of_attractors & \
                                                                      self.dic_var_cnf[str(termino_aux) + "_" + str(
                                                                          number_of_transitions - 1)]
                        else:
                            boolean_expression_clause_of_attractors = boolean_expression_clause_of_attractors & - \
                                self.dic_var_cnf[str(termino_aux) + "_" + str(number_of_transitions - 1)]
                    cont_termino = cont_termino + 1
                if cont_clause == 0:
                    boolean_function_of_attractors = -boolean_expression_clause_of_attractors
                else:
                    boolean_function_of_attractors = boolean_function_of_attractors & - boolean_expression_clause_of_attractors
                cont_clause = cont_clause + 1
            boolean_function = boolean_function & boolean_function_of_attractors
            # print(boolean_function)
        return boolean_function

    def count_state_repeat(self, state, path_solution):
        # input type [[],[],...[]]
        number_of_times = 0
        for element in path_solution:
            if element == state:
                number_of_times = number_of_times + 1
        return number_of_times

    # def find_local_attractor_by_permutation(self, permutation):
    #     # format List = (permutation,[attractors])
    #     l_permutation_attractor = [permutation, []]
    #
    #     # print "BEGIN TO FIND ATTRACTORS"
    #     # create boolean expression initial with transition = n
    #     set_of_attractors = []
    #     v_num_transitions = 3
    #     l_attractors = []
    #     l_attractors_clauses = []
    #
    #     # REPEAT CODE
    #     v_bool_function = self.generate_boolean_formulation(v_num_transitions, l_attractors_clauses, permutation)
    #     m_response_sat = []
    #     o_solver = Minisat()
    #     o_solution = o_solver.solve(v_bool_function)
    #
    #     # print(oRDD.number_of_v_total)
    #     if o_solution.success:
    #         for j in range(0, v_num_transitions):
    #             m_response_sat.append([])
    #             for i in self.list_of_v_total:
    #                 # print("TEST")
    #                 # print(str(i)+"_"+str(j))
    #                 # print(oRDD.dic_var_cnf)
    #                 # print("TEST")
    #                 m_response_sat[j].append(o_solution[self.dic_var_cnf[str(i) + "_" + str(j)]])
    #     else:
    #         # print(" ")
    #         print("The expression cannot be satisfied")
    #
    #     # BLOCK ATTRACTORS
    #     m_auxiliary_sat = []
    #     if len(m_response_sat) != 0:
    #         # TRANSFORM BOOLEAN TO MATRIX BOOLEAN RESPONSE
    #         for j in range(0, v_num_transitions):
    #             matrix_aux_sat = []
    #             for i in range(0, self.number_of_v_total):
    #                 if m_response_sat[j][i]:
    #                     matrix_aux_sat.append("1")
    #                 else:
    #                     matrix_aux_sat.append("0")
    #             m_auxiliary_sat.append(matrix_aux_sat)
    #         # m_boolean_res = m_auxiliary_sat
    #     m_boolean_res = m_auxiliary_sat
    #     # BLOCK ATTRACTORS
    #     # REPEAT CODE
    #
    #     while len(m_boolean_res) > 0:
    #         # print ("path")
    #         # print (m_boolean_res)
    #         # print ("path")
    #         path_solution = []
    #         for path_transition in m_boolean_res:
    #             path_solution.append(path_transition)
    #
    #         # new list of state attractors
    #         l_news_estates_attractor = []
    #         # check attractors
    #         for v_state in path_solution:
    #             v_state_count = self.count_state_repeat(v_state, path_solution)
    #             if v_state_count > 1:
    #                 attractor_begin = path_solution.index(v_state) + 1
    #                 attractor_end = path_solution[attractor_begin:].index(v_state)
    #                 l_news_estates_attractor = path_solution[attractor_begin - 1:(attractor_begin + attractor_end)]
    #                 l_attractors = l_attractors + l_news_estates_attractor
    #                 # add attractors like list of list
    #                 set_of_attractors.append(l_news_estates_attractor)
    #                 break
    #
    #         # duplicate the number of transitions"
    #         if len(l_news_estates_attractor) == 0:
    #             v_num_transitions = v_num_transitions * 2
    #
    #         # transform list of attractors to clauses
    #         for clause_attractor in l_attractors:
    #             clause_variable = []
    #             cont_variable = 0
    #             for estate_attractor in clause_attractor:
    #                 if estate_attractor == "0":
    #                     clause_variable.append("-" + str(self.list_of_v_total[cont_variable]))
    #                 else:
    #                     clause_variable.append(str(self.list_of_v_total[cont_variable]))
    #                 cont_variable = cont_variable + 1
    #             l_attractors_clauses.append(clause_variable)
    #
    #         # print l_attractors_clauses
    #         # REPEAT CODE
    #         v_bool_function = self.generate_boolean_formulation(v_num_transitions, l_attractors_clauses, permutation)
    #         m_response_sat = []
    #         o_solver = Minisat()
    #         o_solution = o_solver.solve(v_bool_function)
    #
    #         if o_solution.success:
    #             for j in range(0, v_num_transitions):
    #                 m_response_sat.append([])
    #                 for i in self.list_of_v_total:
    #                     m_response_sat[j].append(o_solution[self.dic_var_cnf[str(i) + "_" + str(j)]])
    #         else:
    #             # print(" ")
    #             print("The expression cannot be satisfied")
    #
    #         # BLOCK ATTRACTORS
    #         m_auxiliary_sat = []
    #         if len(m_response_sat) != 0:
    #             # TRANSFORM BOOLEAN TO MATRIX BOOLEAN RESPONSE
    #             for j in range(0, v_num_transitions):
    #                 matrix_aux_sat = []
    #                 for i in range(0, self.number_of_v_total):
    #                     if m_response_sat[j][i]:
    #                         matrix_aux_sat.append("1")
    #                     else:
    #                         matrix_aux_sat.append("0")
    #                 m_auxiliary_sat.append(matrix_aux_sat)
    #             # m_boolean_res = m_auxiliary_sat
    #         m_boolean_res = m_auxiliary_sat
    #         # BLOCK ATTRACTORS
    #         # REPEAT CODE
    #     l_permutation_attractor[1] = set_of_attractors
    #     self.list_permutations_attractors.append(l_permutation_attractor)

    @staticmethod
    def generateBooleanFormulationSatispy(oRDD, number_of_transitions, l_atractors_clausules, l_signal_coupling):
        # create dictionary of cnf variables!!
        for variable in oRDD.list_of_v_total:
            for transition_c in range(0, number_of_transitions):
                oRDD.dic_var_cnf[str(variable) + "_" + str(transition_c)] = Variable(
                    str(variable) + "_" + str(transition_c))

        # transition_aux = 0
        cont_transition = 0
        boolean_function = Variable("0_0")
        for transition in range(1, number_of_transitions):
            # transition_aux = transition
            cont_clausula_global = 0
            boolean_expresion_equivalence = Variable("0_0")
            for oVariableModel in oRDD.description_variables:
                cont_clausula = 0
                boolean_expresion_clausule_global = Variable("0_0")
                for clausula in oVariableModel.cnf_function:
                    boolean_expresion_clausule = Variable("0_0")
                    cont_termino = 0
                    for termino in clausula:
                        termino_aux = abs(int(termino))
                        if (cont_termino == 0):
                            if (str(termino)[0] != "-"):
                                boolean_expresion_clausule = oRDD.dic_var_cnf[
                                    str(termino_aux) + "_" + str(transition - 1)]
                            else:
                                boolean_expresion_clausule = -oRDD.dic_var_cnf[
                                    str(termino_aux) + "_" + str(transition - 1)]
                        else:
                            if (str(termino)[0] != "-"):
                                boolean_expresion_clausule = oRDD.dic_var_cnf[str(termino_aux) + "_" + str(
                                    transition - 1)] | boolean_expresion_clausule
                            else:
                                boolean_expresion_clausule = -oRDD.dic_var_cnf[
                                    str(termino_aux) + "_" + str(transition - 1)] | boolean_expresion_clausule
                        cont_termino = cont_termino + 1
                    if (cont_clausula) == 0:
                        boolean_expresion_clausule_global = boolean_expresion_clausule
                    else:
                        boolean_expresion_clausule_global = boolean_expresion_clausule_global & boolean_expresion_clausule
                    cont_clausula = cont_clausula + 1
                if cont_clausula_global == 0:
                    boolean_expresion_equivalence = oRDD.dic_var_cnf[str(oVariableModel.name_variable) + "_" + str(
                        transition)] >> boolean_expresion_clausule_global
                    boolean_expresion_equivalence = boolean_expresion_equivalence & (
                            boolean_expresion_clausule_global >> oRDD.dic_var_cnf[
                        str(oVariableModel.name_variable) + "_" + str(transition)])
                else:
                    boolean_expresion_equivalence = boolean_expresion_equivalence & (oRDD.dic_var_cnf[
                                                                                         str(oVariableModel.name_variable) + "_" + str(
                                                                                             transition)] >> boolean_expresion_clausule_global)
                    boolean_expresion_equivalence = boolean_expresion_equivalence & (
                            boolean_expresion_clausule_global >> oRDD.dic_var_cnf[
                        str(oVariableModel.name_variable) + "_" + str(transition)])
                if (oVariableModel.cnf_function == []):
                    print("ENTRO CASO ATIPICO")
                    boolean_function = boolean_function & (
                            oRDD.dic_var_cnf[str(oVariableModel.name_variable) + "_" + str(transition)] | -
                    oRDD.dic_var_cnf[str(oVariableModel.name_variable) + "_" + str(transition)])
                cont_clausula_global = cont_clausula_global + 1
            if cont_transition == 0:
                boolean_function = boolean_expresion_equivalence
            else:
                boolean_function = boolean_function & boolean_expresion_equivalence
            # VALIDAR LOS GENES EN BLANCO
            cont_transition = cont_transition + 1

        # ASSING VALUES FOR PERMUTATIONS
        cont_permutacion = 0
        for elemento in oRDD.list_of_v_exterm:
            # print oRDD.list_of_v_exterm
            for v_transition in range(0, number_of_transitions):
                # print l_signal_coupling[cont_permutacion]
                if l_signal_coupling[cont_permutacion] == "0":
                    boolean_function = boolean_function & -oRDD.dic_var_cnf[str(elemento) + "_" + str(v_transition)]
                    # print (str(elemento) +"_"+ str(v_transition))
                else:
                    boolean_function = boolean_function & oRDD.dic_var_cnf[str(elemento) + "_" + str(v_transition)]
                    # print (str(elemento) +"_"+ str(v_transition))
            cont_permutacion = cont_permutacion + 1

        # add atractors to boolean function
        if (len(l_atractors_clausules) > 0):
            boolean_function_of_atractors = Variable("0_0")
            cont_clausula = 0
            for clausula in l_atractors_clausules:
                boolean_expresion_clausule_of_atractors = Variable("0_0")
                cont_termino = 0
                for termino in clausula:
                    termino_aux = abs(int(termino))
                    # print str(termino_aux) + "_" + str(number_of_transitions-1)
                    if (cont_termino == 0):
                        if (termino[0] != "-"):
                            boolean_expresion_clausule_of_atractors = oRDD.dic_var_cnf[
                                str(termino_aux) + "_" + str(number_of_transitions - 1)]
                        else:
                            boolean_expresion_clausule_of_atractors = -oRDD.dic_var_cnf[
                                str(termino_aux) + "_" + str(number_of_transitions - 1)]
                    else:
                        if (termino[0] != "-"):
                            boolean_expresion_clausule_of_atractors = boolean_expresion_clausule_of_atractors & \
                                                                      oRDD.dic_var_cnf[str(termino_aux) + "_" + str(
                                                                          number_of_transitions - 1)]
                        else:
                            boolean_expresion_clausule_of_atractors = boolean_expresion_clausule_of_atractors & - \
                                oRDD.dic_var_cnf[str(termino_aux) + "_" + str(number_of_transitions - 1)]
                    cont_termino = cont_termino + 1
                if (cont_clausula) == 0:
                    boolean_function_of_atractors = -boolean_expresion_clausule_of_atractors
                else:
                    boolean_function_of_atractors = boolean_function_of_atractors & - boolean_expresion_clausule_of_atractors
                cont_clausula = cont_clausula + 1
            boolean_function = boolean_function & boolean_function_of_atractors
            # print(boolean_function)
        return boolean_function

    def findLocalAtractorsSATSatispy(oRDD, l_signal_coupling):
        def countStateRepeat(estado, path_solution):
            # input type [[],[],...[]]
            number_of_times = 0
            for elemento in path_solution:
                if elemento == estado:
                    number_of_times = number_of_times + 1
            return number_of_times

        # print "BEGIN TO FIND ATTRACTORS"
        print("NETWORK NUMBER : " + str(oRDD.number_of_rdda) + " PERMUTATION SIGNAL COUPLING: " + l_signal_coupling)
        # create boolean expression initial with "n" transitions
        oRDD.set_of_attractors = []
        v_num_transitions = 3
        l_atractors = []
        l_atractors_clausules = []

        # REPEAT CODE
        v_bool_function = oRDD.generateBooleanFormulationSatispy(oRDD, v_num_transitions, l_atractors_clausules,
                                                                 l_signal_coupling)
        m_respuesta_sat = []
        o_solver = Minisat()
        o_solution = o_solver.solve(v_bool_function)

        # print(oRDD.number_of_v_total)
        if o_solution.success:
            for j in range(0, v_num_transitions):
                m_respuesta_sat.append([])
                for i in oRDD.list_of_v_total:
                    # print("TEST")
                    # print(str(i)+"_"+str(j))
                    # print(oRDD.dic_var_cnf)
                    # print("TEST")


                    print(oRDD.dic_var_cnf.get(f'{i}_{j}'))
                    print("======================================")
                    print(oRDD.dic_var_cnf.keys())
                    print(oRDD.dic_var_cnf.values())
                    print(o_solution.varmap)
                    print("Length 1:", len(oRDD.dic_var_cnf))
                    print("Length 2:", len(o_solution.varmap.keys()))
                    #print(f"{i}_{j}")
                    m_respuesta_sat[j].append(o_solution[oRDD.dic_var_cnf[f'{i}_{j}']])
        else:
            # print(" ")
            print("The expression cannot be satisfied")

        # BLOCK ATRACTORS
        m_auxliar_sat = []
        if (len(m_respuesta_sat) != 0):
            # TRANFORM BOOLEAN TO MATRIZ BOOLEAN RESPONSE
            for j in range(0, v_num_transitions):
                matriz_aux_sat = []
                for i in range(0, oRDD.number_of_v_total):
                    if m_respuesta_sat[j][i] == True:
                        matriz_aux_sat.append("1")
                    else:
                        matriz_aux_sat.append("0")
                m_auxliar_sat.append(matriz_aux_sat)
            # m_resp_booleana = m_auxliar_sat
        m_resp_booleana = m_auxliar_sat
        # BLOCK ATRACTORS
        # REPEAT CODE

        while (len(m_resp_booleana) > 0):
            # print ("path")
            # print (m_resp_booleana)
            # print ("path")
            path_solution = []
            for path_trasition in m_resp_booleana:
                path_solution.append(path_trasition)

            # new list of state attractors
            l_news_estates_atractor = []
            # check atractors
            for v_state in path_solution:
                v_state_count = countStateRepeat(v_state, path_solution)
                if (v_state_count > 1):
                    atractor_begin = path_solution.index(v_state) + 1
                    atractor_end = path_solution[atractor_begin:].index(v_state)
                    l_news_estates_atractor = path_solution[atractor_begin - 1:(atractor_begin + atractor_end)]
                    l_atractors = l_atractors + l_news_estates_atractor
                    # add atractors like list of list
                    oRDD.set_of_attractors.append(l_news_estates_atractor)
                    break

            # print oRDD.set_of_attractors
            if len(l_news_estates_atractor) == 0:
                # print ("DOBLANDO")
                v_num_transitions = v_num_transitions * 2

            # TRANFORM LIST OF ATRACTORS TO CLAUSULES
            for clausule_atractor in l_atractors:
                clausule_variable = []
                cont_variable = 0
                for estate_atractor in clausule_atractor:
                    if (estate_atractor == "0"):
                        clausule_variable.append("-" + str(oRDD.list_of_v_total[cont_variable]))
                    else:
                        clausule_variable.append(str(oRDD.list_of_v_total[cont_variable]))
                    cont_variable = cont_variable + 1
                l_atractors_clausules.append(clausule_variable)

            # print l_atractors_clausules
            # REPEAT CODE
            v_bool_function = oRDD.generateBooleanFormulationSatispy(oRDD, v_num_transitions, l_atractors_clausules,
                                                                     l_signal_coupling)
            m_respuesta_sat = []
            o_solver = Minisat()
            o_solution = o_solver.solve(v_bool_function)

            if o_solution.success:
                for j in range(0, v_num_transitions):
                    m_respuesta_sat.append([])
                    for i in oRDD.list_of_v_total:
                        m_respuesta_sat[j].append(o_solution[oRDD.dic_var_cnf[f'{i}_{j}']])
            else:
                # print(" ")
                print("The expression cannot be satisfied")

            # BLOCK ATRACTORS
            m_auxliar_sat = []
            if (len(m_respuesta_sat) != 0):
                # TRANFORM BOOLEAN TO MATRIZ BOOLEAN RESPONSE
                for j in range(0, v_num_transitions):
                    matriz_aux_sat = []
                    for i in range(0, oRDD.number_of_v_total):
                        if m_respuesta_sat[j][i] == True:
                            matriz_aux_sat.append("1")
                        else:
                            matriz_aux_sat.append("0")
                    m_auxliar_sat.append(matriz_aux_sat)
                # m_resp_booleana = m_auxliar_sat
            m_resp_booleana = m_auxliar_sat
            # BLOCK ATRACTORS
            # REPEAT CODE

        # print oRDD.set_of_attractors
        # print(" ")
        # print ("END OF FIND ATRACTORS")
        return oRDD.set_of_attractors

#    @staticmethod
#    @ray.remote
    def findLocalAtractorsSATSatispy_ray(oRDD, l_signal_coupling):
        def countStateRepeat(estado, path_solution):
            # input type [[],[],...[]]
            number_of_times = 0
            for elemento in path_solution:
                if elemento == estado:
                    number_of_times = number_of_times + 1
            return number_of_times

        # print "BEGIN TO FIND ATTRACTORS"
        print("RED NUMBER : " + str(oRDD.number_of_rdda) + " PERMUTATION SIGNAL COUPLING: " + l_signal_coupling)
        # create boolean expresion initial with transition = n
        oRDD.set_of_attractors = []
        v_num_transitions = 3
        l_atractors = []
        l_atractors_clausules = []

        # REPEAT CODE
        v_bool_function = oRDD.generateBooleanFormulationSatispy(oRDD, v_num_transitions, l_atractors_clausules,
                                                                 l_signal_coupling)
        m_respuesta_sat = []
        o_solver = Minisat()
        o_solution = o_solver.solve(v_bool_function)

        # print(oRDD.number_of_v_total)
        if o_solution.success:
            for j in range(0, v_num_transitions):
                m_respuesta_sat.append([])
                for i in oRDD.list_of_v_total:
                    # print("TEST")
                    # print(str(i)+"_"+str(j))
                    # print(oRDD.dic_var_cnf)
                    # print("TEST")
                    m_respuesta_sat[j].append(o_solution[oRDD.dic_var_cnf[str(i) + "_" + str(j)]])
        else:
            # print(" ")
            print("The expression cannot be satisfied")

        # BLOCK ATRACTORS
        m_auxliar_sat = []
        if (len(m_respuesta_sat) != 0):
            # TRANFORM BOOLEAN TO MATRIZ BOOLEAN RESPONSE
            for j in range(0, v_num_transitions):
                matriz_aux_sat = []
                for i in range(0, oRDD.number_of_v_total):
                    if m_respuesta_sat[j][i] == True:
                        matriz_aux_sat.append("1")
                    else:
                        matriz_aux_sat.append("0")
                m_auxliar_sat.append(matriz_aux_sat)
            # m_resp_booleana = m_auxliar_sat
        m_resp_booleana = m_auxliar_sat
        # BLOCK ATRACTORS
        # REPEAT CODE

        while (len(m_resp_booleana) > 0):
            # print ("path")
            # print (m_resp_booleana)
            # print ("path")
            path_solution = []
            for path_trasition in m_resp_booleana:
                path_solution.append(path_trasition)

            # new list of state attractors
            l_news_estates_atractor = []
            # check atractors
            for v_state in path_solution:
                v_state_count = countStateRepeat(v_state, path_solution)
                if (v_state_count > 1):
                    atractor_begin = path_solution.index(v_state) + 1
                    atractor_end = path_solution[atractor_begin:].index(v_state)
                    l_news_estates_atractor = path_solution[atractor_begin - 1:(atractor_begin + atractor_end)]
                    l_atractors = l_atractors + l_news_estates_atractor
                    # add atractors like list of list
                    oRDD.set_of_attractors.append(l_news_estates_atractor)
                    break

            # print oRDD.set_of_attractors
            if len(l_news_estates_atractor) == 0:
                # print ("DOBLANDO")
                v_num_transitions = v_num_transitions * 2

            # TRANFORM LIST OF ATRACTORS TO CLAUSULES
            for clausule_atractor in l_atractors:
                clausule_variable = []
                cont_variable = 0
                for estate_atractor in clausule_atractor:
                    if (estate_atractor == "0"):
                        clausule_variable.append("-" + str(oRDD.list_of_v_total[cont_variable]))
                    else:
                        clausule_variable.append(str(oRDD.list_of_v_total[cont_variable]))
                    cont_variable = cont_variable + 1
                l_atractors_clausules.append(clausule_variable)

            # print l_atractors_clausules
            # REPEAT CODE
            v_bool_function = oRDD.generateBooleanFormulationSatispy(oRDD, v_num_transitions, l_atractors_clausules,
                                                                     l_signal_coupling)
            m_respuesta_sat = []
            o_solver = Minisat()
            o_solution = o_solver.solve(v_bool_function)

            if o_solution.success:
                for j in range(0, v_num_transitions):
                    m_respuesta_sat.append([])
                    for i in oRDD.list_of_v_total:
                        m_respuesta_sat[j].append(o_solution[oRDD.dic_var_cnf[str(i) + "_" + str(j)]])
            else:
                # print(" ")
                print("The expression cannot be satisfied")

            # BLOCK ATRACTORS
            m_auxliar_sat = []
            if (len(m_respuesta_sat) != 0):
                # TRANFORM BOOLEAN TO MATRIZ BOOLEAN RESPONSE
                for j in range(0, v_num_transitions):
                    matriz_aux_sat = []
                    for i in range(0, oRDD.number_of_v_total):
                        if m_respuesta_sat[j][i] == True:
                            matriz_aux_sat.append("1")
                        else:
                            matriz_aux_sat.append("0")
                    m_auxliar_sat.append(matriz_aux_sat)
                # m_resp_booleana = m_auxliar_sat
            m_resp_booleana = m_auxliar_sat
            # BLOCK ATRACTORS
            # REPEAT CODE

        # print oRDD.set_of_attractors
        # print(" ")
        # print ("END OF FIND ATRACTORS")
        return oRDD.set_of_attractors
