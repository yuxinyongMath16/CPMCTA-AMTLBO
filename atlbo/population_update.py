# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2023年07月23日
tlbo算法种群更新部分
"""
import copy
import random
import population_generation
import math
import MAP
import fitness_calculation
import numpy as np


# 资源更新函数,update_type = 1弹药增加，update_type = 0 弹药减少,资源集合，编号，弹药数量，类型
def resource_update(resource, num, ammo_num, update_type):
    if update_type == 0:
        resource[2][num - 1] = resource[2][num - 1] - ammo_num
        if resource[2][num - 1] == 0:
            resource[1].remove(num)
    else:
        resource[2][num - 1] = resource[2][num - 1] + ammo_num
        if resource[2][num - 1] == ammo_num:
            resource[1].append(num)
    return resource


def calculate_parameter(current_iter, max_iter):
    a = 2 - 2 * (current_iter / max_iter)
    gama1 = random.random()
    gama2 = random.random()
    parameter_a = 2 * a * gama1 - a
    parameter_c = 2 * a * gama2
    return parameter_a, parameter_c


def sorting_solution_set(solutions, fitness, resources, f1, f2):
    sort_resources = []
    # print('适应度函数', fitness)
    sort_fitness = np.argsort(fitness)
    solution_fit_set = []
    # print('初始种群是', solutions)
    # print('初始的资源集合', resources)
    # print('适应度排序结果是', sort_fitness)
    for i in range(len(solutions)):
        solution_fit_set.append([solutions[sort_fitness[i]], fitness[sort_fitness[i]], f1[sort_fitness[i]], f2[sort_fitness[i]]])
        sort_resources.append(resources[sort_fitness[i]])
    return solution_fit_set, sort_resources


# 选择教师与分组
def select_teacher(solution_fitness, tea_num):
    # print('选择教师', solution_fitness[1][-1], solution_fitness[1])
    fitness_length = solution_fitness[-1][1] - solution_fitness[0][1]
    # print('最大值', solution_fitness[0][1], solution_fitness[-1][1])
    solution_population = len(solution_fitness)
    avg_interval = fitness_length / tea_num
    teacher_index = []
    teacher_fitness = []
    for i in range(tea_num):
        if i == 0:
            tea_fitness = solution_fitness[0][1]
        else:
            tea_fitness = solution_fitness[0][1] + i * avg_interval + (random.random()-0.5)*avg_interval/8
        teacher_fitness.append(tea_fitness)
    # print('教师适应度序列', teacher_fitness)
    for p in range(tea_num):
        for q in range(solution_population - 1):
            if solution_fitness[q][1] <= teacher_fitness[p] <= solution_fitness[q+1][1]:
                new_index = q
                while True:
                    if new_index not in teacher_index:
                        teacher_index.append(new_index)
                        break
                    else:
                        new_index += 1
                break
    teacher_index.append(solution_population-1)
    return teacher_index


# 计算每组的中等水平
def calculate_middle_student(teacher_index):
    middle_index = []
    for i in range(len(teacher_index)-1):
        mid_index = int((teacher_index[i] + teacher_index[i+1])/2)
        middle_index.append(mid_index)
    return middle_index


def calculate_crossover_individual(current_num, teacher_index, middle_index, cal_type):
    for p in range(len(teacher_index)-1):
        if teacher_index[p] < current_num <= teacher_index[p+1]:
            if cal_type == 1:
                return middle_index[p]
            else:
                return teacher_index[p]


# 单点交叉
def single_point_crossover(solution1_copy, solution2_copy, uavs, targets):
    # 一些初始变量定义，以及交叉位置确认
    solution1 = copy.deepcopy(solution1_copy)
    solution2 = copy.deepcopy(solution2_copy)
    new_solution = []
    solution_num = len(solution1)
    start_point = random.randint(0, solution_num - 1)
    # 生成初始资源约束集，并且根据前半段染色体的情况，更新资源约束集
    new_resource = population_generation.resource_init(uavs)
    for i in range(start_point):
        if solution1[i][1] == 2:
            new_resource = resource_update(new_resource, solution1[i][2], 1, 0)
            new_solution.append(solution1[i])
        else:
            new_solution.append(solution1[i])
    # 将solution2中对应目标的uav提取出来
    solution2_uav = [[] for i in range(len(targets))]
    for i in range(len(solution2)):
        if solution2[i][2] not in solution2_uav[solution2[i][0]-1]:
            solution2_uav[solution2[i][0]-1].append(solution2[i][2])
    # print('任务的无人机集合', solution2_uav)
    # print('交叉前,解的编码', new_solution)
    # print('交叉前,资源约束集', new_resource)
    # print('交叉前,原始解的编码', solution1)
    # 单点交叉，将染色体后面的信息用solution2中的信息替代
    for i in range(solution_num - start_point):
        current_target = solution1[i + start_point][0]
        solution_part = solution1[i + start_point]
        # print('当前目标是', current_target)
        if solution1[i + start_point][1] == 2:
            attack_inter = []
            for p in range(len(solution2_uav[current_target - 1])):
                if solution2_uav[current_target - 1][p] in new_resource[1]:
                    attack_inter.append(solution2_uav[current_target - 1][p])
            # print('对目标执行任务的集合', solution2_uav[current_target - 1], '攻击任务资源约束集', new_resource[1], '交集', attack_inter)
            if len(attack_inter) != 0:
                rand_num = random.randint(0, len(attack_inter) - 1)
                dispatch_num = attack_inter[rand_num]
                new_resource = resource_update(new_resource, dispatch_num, 1, 0)
                solution_part[2] = dispatch_num
            else:
                rand_num = random.randint(0, len(new_resource[1]) - 1)
                dispatch_num = new_resource[1][rand_num]
                new_resource = resource_update(new_resource, dispatch_num, 1, 0)
                solution_part[2] = dispatch_num
        else:
            detect_inter = []
            for p in range(len(solution2_uav[current_target - 1])):
                if solution2_uav[current_target - 1][p] in new_resource[0]:
                    detect_inter.append(solution2_uav[current_target - 1][p])
            # print('对目标执行任务的集合', solution2_uav[current_target - 1], '侦查任务资源约束集', new_resource[0], '交集', detect_inter)
            if len(detect_inter) != 0:
                rand_num = random.randint(0, len(detect_inter) - 1)
                dispatch_num = detect_inter[rand_num]
                solution_part[2] = dispatch_num
            else:
                rand_num = random.randint(0, len(new_resource[0]) - 1)
                dispatch_num = new_resource[0][rand_num]
                solution_part[2] = dispatch_num
        new_solution.append(solution_part)
    # print('交叉后,解的编码', new_solution)
    # print('交叉后,资源约束集', new_resource)
    # 第四步，将染色体根据无人机编号顺序重新排列
    new_solution1 = sorted(new_solution, key=(lambda x: x[2]))
    # print('排序后,解的编码', new_solution)
    return new_solution1, new_resource


def attack_exchange(chromosome, resource, num):
    random_num = random.randint(0, len(resource[1]) - 1)
    exchange_uav_num = resource[1][random_num]
    resource = resource_update(resource, chromosome[num][2], 1, 1)
    chromosome[num][2] = exchange_uav_num
    resource = resource_update(resource, exchange_uav_num, 1, 0)
    return chromosome, resource


def detect_exchange(chromosome, resource, num):
    random_num = random.randint(0, len(resource[0]) - 1)
    exchange_uav_num = resource[0][random_num]
    chromosome[num][2] = exchange_uav_num
    return chromosome, resource


def change_uav_num(chromosome, resource, num):
    if chromosome[num][1] == 2:
        chromosome, resource = attack_exchange(chromosome, resource, num)
    else:
        chromosome, resource = detect_exchange(chromosome, resource, num)
    return chromosome, resource


# 变异函数
def mutation(chromosome, resource):
    PM = 1
    # DNA_num = random.randint(0, len(chromosomes) - 1)
    m_chromosome = copy.deepcopy(chromosome)
    m_resource = copy.deepcopy(resource)
    # 一、产生随机数如果大于0.1则对该染色体执行对随机目标改变执行无人机
    rand_mutation1 = random.random()
    # 有0.1的概率对染色体执行下列变异操作
    if rand_mutation1 < PM:
        # print('执行改变随机任务执行UAV编号的变异')
        random_num1 = random.randint(0, len(m_chromosome) - 1)
        # print('改变随机任务执行UAV编号前', m_chromosome)
        m_chromosome, m_resource = change_uav_num(m_chromosome, m_resource, random_num1)
        # print('改变随机任务执行UAV编号后', m_chromosome)
        m_chromosome = sorted(m_chromosome, key=(lambda x: x[2]))
    # 二、 改变随机选择的无人机的任务顺序
    rand_mutation2 = random.random()
    if rand_mutation2 < PM:
        # print('执行改变随机无人机执行任务顺序的变异')
        taskmutapos = random.randint(0, len(m_chromosome) - 1)
        taskmutUAV = m_chromosome[taskmutapos][2]
        jishu = -1
        randDNAset = []
        # print('改变随机无人机执行任务顺序前', m_chromosome)
        for i in range(len(m_chromosome)):
            if m_chromosome[i][2] == taskmutUAV and jishu == -1:
                startmutUAV = i
                randDNAset.append(m_chromosome[i])
                jishu = jishu + 1
            elif m_chromosome[i][2] == taskmutUAV and jishu != -1:
                randDNAset.append(m_chromosome[i])
                jishu = jishu + 1
        random.shuffle(randDNAset)
        for j in range(jishu + 1):
            m_chromosome[j + startmutUAV] = randDNAset[j]
        # print('改变随机无人机执行任务顺序后', m_chromosome)
    return m_chromosome, m_resource


# 变异函数
def mutation1(chromosome, resource):
    # DNA_num = random.randint(0, len(chromosomes) - 1)
    m_chromosome = copy.deepcopy(chromosome)
    m_resource = copy.deepcopy(resource)
    # 一、产生随机数如果大于0.1则对该染色体执行对随机目标改变执行无人机
    rand_mutation1 = random.random()
    # 有0.1的概率对染色体执行下列变异操作
    if rand_mutation1 <= 0.25:
        # print('执行改变随机任务执行UAV编号的变异')
        random_num1 = random.randint(0, len(m_chromosome) - 1)
        # print('改变随机任务执行UAV编号前', m_chromosome)
        m_chromosome, m_resource = change_uav_num(m_chromosome, m_resource, random_num1)
        # print('改变随机任务执行UAV编号后', m_chromosome)
        m_chromosome = sorted(m_chromosome, key=(lambda x: x[2]))
    elif 0.25 < rand_mutation1 <= 0.5:
        # print('执行改变随机无人机执行任务顺序的变异')
        taskmutapos = random.randint(0, len(m_chromosome) - 1)
        taskmutUAV = m_chromosome[taskmutapos][2]
        jishu = -1
        randDNAset = []
        # print('改变随机无人机执行任务顺序前', m_chromosome)
        for i in range(len(m_chromosome)):
            if m_chromosome[i][2] == taskmutUAV and jishu == -1:
                startmutUAV = i
                randDNAset.append(m_chromosome[i])
                jishu = jishu + 1
            elif m_chromosome[i][2] == taskmutUAV and jishu != -1:
                randDNAset.append(m_chromosome[i])
                jishu = jishu + 1
        random.shuffle(randDNAset)
        for j in range(jishu + 1):
            m_chromosome[j + startmutUAV] = randDNAset[j]
        # print('改变随机无人机执行任务顺序后', m_chromosome)
    elif 0.5 < rand_mutation1 <= 0.75:
        # print('执行改变随机任务执行UAV编号的变异')
        random_num1 = random.randint(0, len(m_chromosome) - 1)
        # print('改变随机任务执行UAV编号前', m_chromosome)
        m_chromosome, m_resource = change_uav_num(m_chromosome, m_resource, random_num1)
        # print('改变随机任务执行UAV编号后', m_chromosome)
        m_chromosome = sorted(m_chromosome, key=(lambda x: x[2]))
        # print('执行改变随机无人机执行任务顺序的变异')
        taskmutapos = random.randint(0, len(m_chromosome) - 1)
        taskmutUAV = m_chromosome[taskmutapos][2]
        jishu = -1
        randDNAset = []
        # print('改变随机无人机执行任务顺序前', m_chromosome)
        for i in range(len(m_chromosome)):
            if m_chromosome[i][2] == taskmutUAV and jishu == -1:
                startmutUAV = i
                randDNAset.append(m_chromosome[i])
                jishu = jishu + 1
            elif m_chromosome[i][2] == taskmutUAV and jishu != -1:
                randDNAset.append(m_chromosome[i])
                jishu = jishu + 1
        random.shuffle(randDNAset)
        for j in range(jishu + 1):
            m_chromosome[j + startmutUAV] = randDNAset[j]
        # print('改变随机无人机执行任务顺序后', m_chromosome)
    return m_chromosome, m_resource


def calculate_parameter_tf(solution_fit_set, current_index, teacher_index):
    tf_part1 = 0
    # print('教师集合', teacher_index)
    # print('当前编号集合', current_index)
    for p in range(len(teacher_index)-1):
        if teacher_index[p] < current_index <= teacher_index[p+1]:
            current_tea = teacher_index[p]
    tf_part1 = solution_fit_set[current_index][1]/solution_fit_set[current_tea][1]
    parameter_tf = random.random() + tf_part1
    return parameter_tf


def calculation_number_teacher(init_tea_num, curr_iter, iter_num):
    return math.ceil(init_tea_num*(1-((curr_iter-1)/iter_num)))


def calculation_population_status(solution_fit_set):
    sum_fitness = 0
    for i in range(len(solution_fit_set)):
        sum_fitness += solution_fit_set[i][1]
    average_fitness = sum_fitness/len(solution_fit_set)
    population_status = len(solution_fit_set)
    for j in range(len(solution_fit_set)-1):
        if solution_fit_set[j][1] <= average_fitness <= solution_fit_set[j+1][1]:
            population_status = j+1
    if population_status <= len(solution_fit_set)/2:
        return 0
    else:
        return 1


def teach_phase_population(solution_fit_set, sort_resources, uavs, targets, Obstacles, init_tea_num, curr_iter, iter_num, threat_r):
    teach_phase_solutions = []
    teach_phase_fitness = []
    teach_phase_resources = []
    teach_phase_f1 = []
    teach_phase_f2 = []
    # print('解序列排序', solution_fit_set)
    tea_num = calculation_number_teacher(init_tea_num, curr_iter, iter_num)
    # print('教师数量#######################', tea_num)
    teacher_index = select_teacher(solution_fit_set, tea_num)
    teacher_copy = [teacher_index[i] for i in range(len(teacher_index)-1)]
    # print('复制教师集合', teacher_copy)
    middle_index = calculate_middle_student(teacher_index)
    # print('教师集合', teacher_index)
    for i in range(len(teacher_index)-1):
        teach_phase_solutions.append(copy.deepcopy(solution_fit_set[teacher_index[i]][0]))
        teach_phase_fitness.append(copy.deepcopy(solution_fit_set[teacher_index[i]][1]))
        teach_phase_resources.append(copy.deepcopy(sort_resources[i]))
        teach_phase_f1.append(copy.deepcopy(solution_fit_set[teacher_index[i]][2]))
        teach_phase_f2.append(copy.deepcopy(solution_fit_set[teacher_index[i]][3]))
    for i in range(len(solution_fit_set)):
        # 非教师个体交叉，教师个体不参加交叉
        if i not in teacher_copy:
            parameter_tf = calculate_parameter_tf(solution_fit_set, i, teacher_index)
            parameter_r1 = random.random()
            # 教阶段
            # 学习率为1，与平均水平交叉
            if parameter_tf <= 0.66:
                if parameter_r1 >= 0.5:
                    cross_teacher = calculate_crossover_individual(i, teacher_index, middle_index, 1)
                    new_solution, new_resource = single_point_crossover(solution_fit_set[cross_teacher][0],
                                                                        solution_fit_set[i][0], uavs, targets)
                    new_fitness, _, _, new_f1, new_f2 = fitness_calculation.fitness([new_solution], targets, uavs, Obstacles, threat_r)
                    if new_fitness[0] <= solution_fit_set[i][1]:
                        teach_phase_solutions.append(new_solution)
                        teach_phase_fitness.append(new_fitness[0])
                        teach_phase_resources.append(new_resource)
                        teach_phase_f1.append(new_f1[0])
                        teach_phase_f2.append(new_f2[0])
                    else:
                        teach_phase_solutions.append(solution_fit_set[i][0])
                        teach_phase_fitness.append(solution_fit_set[i][1])
                        teach_phase_resources.append(sort_resources[i])
                        teach_phase_f1.append(solution_fit_set[i][2])
                        teach_phase_f2.append(solution_fit_set[i][3])
                else:
                    teach_phase_solutions.append(solution_fit_set[i][0])
                    teach_phase_fitness.append(solution_fit_set[i][1])
                    teach_phase_fitness.append(sort_resources[i])
                    teach_phase_f1.append(solution_fit_set[i][2])
                    teach_phase_f2.append(solution_fit_set[i][3])
            elif 0.66 < parameter_tf <= 1.32:
                if parameter_r1 >= 0.5:
                    cross_teacher = calculate_crossover_individual(i, teacher_index, middle_index, 2)
                    new_solution, new_resource = single_point_crossover(solution_fit_set[cross_teacher][0],
                                                                        solution_fit_set[i][0], uavs,
                                                                        targets)
                    new_fitness, _, _, new_f1, new_f2 = fitness_calculation.fitness([new_solution], targets, uavs, Obstacles, threat_r)
                    if new_fitness[0] <= solution_fit_set[i][1]:
                        teach_phase_solutions.append(new_solution)
                        teach_phase_fitness.append(new_fitness[0])
                        teach_phase_resources.append(new_resource)
                        teach_phase_f1.append(new_f1[0])
                        teach_phase_f2.append(new_f2[0])
                    else:
                        teach_phase_solutions.append(solution_fit_set[i][0])
                        teach_phase_fitness.append(solution_fit_set[i][1])
                        teach_phase_resources.append(sort_resources[i])
                        teach_phase_f1.append(solution_fit_set[i][2])
                        teach_phase_f2.append(solution_fit_set[i][3])
                else:
                    teach_phase_solutions.append(solution_fit_set[i][0])
                    teach_phase_fitness.append(solution_fit_set[i][1])
                    teach_phase_resources.append(sort_resources[i])
                    teach_phase_f1.append(solution_fit_set[i][2])
                    teach_phase_f2.append(solution_fit_set[i][3])
            else:
                if parameter_r1 >= 0.5:
                    cross_teacher = calculate_crossover_individual(i, teacher_index, middle_index, 2)
                    new_solution1, _ = single_point_crossover(solution_fit_set[cross_teacher][0],
                                                              solution_fit_set[i][0], uavs,
                                                              targets)
                    new_solution, new_resource = single_point_crossover(solution_fit_set[cross_teacher][0],
                                                                        new_solution1, uavs, targets)
                    new_fitness, _, _, new_f1, new_f2 = fitness_calculation.fitness([new_solution], targets, uavs, Obstacles, threat_r)
                    if new_fitness[0] <= solution_fit_set[i][1]:
                        teach_phase_solutions.append(new_solution)
                        teach_phase_fitness.append(new_fitness[0])
                        teach_phase_resources.append(new_resource)
                        teach_phase_f1.append(new_f1[0])
                        teach_phase_f2.append(new_f2[0])
                    else:
                        teach_phase_solutions.append(solution_fit_set[i][0])
                        teach_phase_fitness.append(solution_fit_set[i][1])
                        teach_phase_resources.append(sort_resources[i])
                        teach_phase_f1.append(solution_fit_set[i][2])
                        teach_phase_f2.append(solution_fit_set[i][3])
                else:
                    teach_phase_solutions.append(solution_fit_set[i][0])
                    teach_phase_fitness.append(solution_fit_set[i][1])
                    teach_phase_resources.append(sort_resources[i])
                    teach_phase_f1.append(solution_fit_set[i][2])
                    teach_phase_f2.append(solution_fit_set[i][3])
    return teach_phase_solutions, teach_phase_fitness, teach_phase_resources, teach_phase_f1, teach_phase_f2


def teach_phase_population1(solution_fit_set, sort_resources, uavs, targets, Obstacles, init_tea_num, curr_iter, iter_num, threat_r):
    teach_phase_solutions = []
    teach_phase_fitness = []
    teach_phase_resources = []
    teach_phase_f1 = []
    teach_phase_f2 = []
    # print('解序列排序', solution_fit_set)
    tea_num = calculation_number_teacher(init_tea_num, curr_iter, iter_num)
    # print('教师数量#######################', tea_num)
    teacher_index = select_teacher(solution_fit_set, tea_num)
    teacher_copy = [teacher_index[i] for i in range(len(teacher_index)-1)]
    # print('复制教师集合', teacher_copy)
    middle_index = calculate_middle_student(teacher_index)
    # print('教师集合', teacher_index)
    for i in range(len(teacher_index)-1):
        teach_phase_solutions.append(copy.deepcopy(solution_fit_set[teacher_index[i]][0]))
        teach_phase_fitness.append(copy.deepcopy(solution_fit_set[teacher_index[i]][1]))
        teach_phase_resources.append(copy.deepcopy(sort_resources[i]))
    for i in range(len(solution_fit_set)):
        # 非教师个体交叉，教师个体不参加交叉
        if i not in teacher_copy:
            parameter_tf = calculate_parameter_tf(solution_fit_set, i, teacher_index)
            parameter_r1 = random.random()
            # 教阶段
            # 学习率为1，与平均水平交叉
            if parameter_tf <= 0.66:
                if parameter_r1 >= 0.5:
                    cross_teacher = calculate_crossover_individual(i, teacher_index, middle_index, 1)
                    new_solution, new_resource = single_point_crossover(solution_fit_set[cross_teacher][0],
                                                                        solution_fit_set[i][0], uavs, targets)
                    new_fitness, _, _, _, _ = fitness_calculation.fitness([new_solution], targets, uavs, Obstacles, threat_r)
                    if new_fitness[0] <= solution_fit_set[i][1]:
                        teach_phase_solutions.append(new_solution)
                        teach_phase_fitness.append(new_fitness[0])
                        teach_phase_resources.append(new_resource)
                    else:
                        teach_phase_solutions.append(solution_fit_set[i][0])
                        teach_phase_fitness.append(solution_fit_set[i][1])
                        teach_phase_resources.append(sort_resources[i])
                else:
                    teach_phase_solutions.append(solution_fit_set[i][0])
                    teach_phase_fitness.append(solution_fit_set[i][1])
                    teach_phase_fitness.append(sort_resources[i])
            elif 0.66 < parameter_tf <= 1.32:
                if parameter_r1 >= 0.5:
                    cross_teacher = calculate_crossover_individual(i, teacher_index, middle_index, 2)
                    new_solution, new_resource = single_point_crossover(solution_fit_set[cross_teacher][0],
                                                                        solution_fit_set[i][0], uavs,
                                                                        targets)
                    new_fitness, _, _, _, _ = fitness_calculation.fitness([new_solution], targets, uavs, Obstacles, threat_r)
                    if new_fitness[0] <= solution_fit_set[i][1]:
                        teach_phase_solutions.append(new_solution)
                        teach_phase_fitness.append(new_fitness[0])
                        teach_phase_resources.append(new_resource)
                    else:
                        teach_phase_solutions.append(solution_fit_set[i][0])
                        teach_phase_fitness.append(solution_fit_set[i][1])
                        teach_phase_resources.append(sort_resources[i])
                else:
                    teach_phase_solutions.append(solution_fit_set[i][0])
                    teach_phase_fitness.append(solution_fit_set[i][1])
                    teach_phase_resources.append(sort_resources[i])
            else:
                teach_phase_solutions.append(solution_fit_set[i][0])
                teach_phase_fitness.append(solution_fit_set[i][1])
                teach_phase_resources.append(sort_resources[i])
    return teach_phase_solutions, teach_phase_fitness, teach_phase_resources


def learn_phase_population(teach_phase_solutions, teach_phase_fitness, teach_phase_resources, uavs, targets, Obstacles, threat_r, f1, f2):
    learn_phase_solutions = []
    learn_phase_fitness = []
    learn_phase_resources = []
    learn_phase_f1 = []
    learn_phase_f2 = []
    # print('教学阶段适应度值', teach_phase_fitness)
    # for i in range(teacher_num):
    #     learn_phase_solutions.append(copy.deepcopy(teach_phase_solutions[i]))
    #     learn_phase_fitness.append(copy.deepcopy(teach_phase_fitness[i]))
    #     learn_phase_resources.append(copy.deepcopy(teach_phase_resources[i]))
    for i in range(len(teach_phase_solutions)):
        parameter_r1 = random.random()
        while True:
            learn_num = random.randint(0, len(teach_phase_solutions)-1)
            if learn_num != i:
                break
        if parameter_r1 < 0.5:
            new_solution, new_resource = single_point_crossover(teach_phase_solutions[i], teach_phase_solutions[learn_num], uavs,
                                                     targets)
            new_fitness, _, _, new_f1, new_f2 = fitness_calculation.fitness([new_solution], targets, uavs, Obstacles, threat_r)
            if new_fitness[0] <= teach_phase_fitness[i]:
                learn_phase_solutions.append(new_solution)
                learn_phase_fitness.append(new_fitness[0])
                learn_phase_resources.append(new_resource)
                learn_phase_f1.append(new_f1[0])
                learn_phase_f2.append(new_f2[0])
            else:
                learn_phase_solutions.append(teach_phase_solutions[i])
                learn_phase_fitness.append(teach_phase_fitness[i])
                learn_phase_resources.append(teach_phase_resources[i])
                learn_phase_f1.append(f1[i])
                learn_phase_f2.append(f2[i])
        else:
            new_solution1, _ = single_point_crossover(teach_phase_solutions[i], teach_phase_solutions[learn_num], uavs,
                                                      targets)
            new_solution, new_resource = single_point_crossover(new_solution1, teach_phase_solutions[learn_num], uavs,
                                                     targets)
            new_fitness, _, _, new_f1, new_f2 = fitness_calculation.fitness([new_solution], targets, uavs, Obstacles, threat_r)
            if new_fitness[0] <= teach_phase_fitness[i]:
                learn_phase_solutions.append(new_solution)
                learn_phase_fitness.append(new_fitness[0])
                learn_phase_resources.append(new_resource)
                learn_phase_f1.append(new_f1[0])
                learn_phase_f2.append(new_f2[0])
            else:
                learn_phase_solutions.append(teach_phase_solutions[i])
                learn_phase_fitness.append(teach_phase_fitness[i])
                learn_phase_resources.append(teach_phase_resources[i])
                learn_phase_f1.append(f1[i])
                learn_phase_f2.append(f2[i])
    return learn_phase_solutions, learn_phase_fitness, learn_phase_resources, learn_phase_f1, learn_phase_f2


def teacher_self_improvement(learn_phase_solutions, learn_phase_fitness, learn_phase_resources, targets, uavs, Obstacles, threat_r, learn_phase_f1, learn_phase_f2):
    for p in range(len(learn_phase_solutions)):
        new_solution, new_resource = mutation(learn_phase_solutions[p], learn_phase_resources[p])
        new_fitness, _, _, new_f1, new_f2 = fitness_calculation.fitness([new_solution], targets, uavs, Obstacles, threat_r)
        if new_fitness[0] <= learn_phase_fitness[p]:
            learn_phase_solutions[p] = copy.deepcopy(new_solution)
            learn_phase_fitness[p] = copy.deepcopy(new_fitness[0])
            learn_phase_resources[p] = copy.deepcopy(new_resource)
            learn_phase_f1[p] = copy.deepcopy(new_f1[0])
            learn_phase_f2[p] = copy.deepcopy(new_f2[0])
    return learn_phase_solutions, learn_phase_fitness, learn_phase_resources, learn_phase_f1, learn_phase_f2


def population_update(solutions, resources, uavs, targets, fitness, Obstacles, init_tea_num, curr_iter, iter_num, threat_r, f1, f2):
    solution_fit_set, sort_resources = sorting_solution_set(solutions, fitness, resources, f1, f2)
    population_status = calculation_population_status(solution_fit_set)
    if population_status == 1:
        first_phase_solutions, first_phase_fitness, first_phase_resources, first_phase_f1, first_phase_f2 = teach_phase_population(solution_fit_set, sort_resources, uavs, targets, Obstacles, init_tea_num, curr_iter, iter_num, threat_r)
        # print('教学阶段长度', len(teach_phase_solutions))
    else:
        first_phase_solutions, first_phase_fitness, first_phase_resources, first_phase_f1, first_phase_f2 = learn_phase_population(solutions, fitness, resources, uavs, targets, Obstacles, threat_r, f1, f2)
        # print('学习阶段长度', len(learn_phase_solutions))
    # new_solutions, new_fitness, new_resources, new_f1, new_f2 = teacher_self_improvement(first_phase_solutions, first_phase_fitness, first_phase_resources, targets, uavs, Obstacles, threat_r, first_phase_f1, first_phase_f2)
    # print('自我提升长度', len(new_solutions))
    return first_phase_solutions, first_phase_fitness, first_phase_resources, first_phase_f1, first_phase_f2


if __name__ == '__main__':
    airport = [[[42000, 18000], 50, math.pi / 2], [[3000, 30000], 50, math.pi / 2], [[29000, 48000], 50, math.pi]]
    Uav = [[[42000, 18000], 1, 80, 0, 250], [[42000, 18000], 3, 60, 5, 220], [[3000, 30000], 2, 70, 2, 200],
           [[29000, 48000], 1, 80, 0, 250, 3], [[29000, 48000], 2, 70, 3, 200, 3]]
    targets = []
    uavs = []
    airports = []
    # obstacles = []
    obstacles = [[1, [[10000, 15000], 2000]], [1, [[15000, 35000], 5000]], [1, [[45000, 25000], 1000]],
                 [1, [[30000, 15000], 2000]], [1, [[35000, 45000], 500]],
                 [2, [[30000, 25000], [35000, 27000], [38000, 31000], [33000, 35000], [26000, 30000]]],
                 [2, [[18000, 21000], [23000, 22000], [24000, 25000], [19000, 26000]]]]
    target = [[[25000, 36000], [1, 2, 3], 40], [[5000, 20000], [1, 2, 3], 60], [[47500, 30000], [1, 2, 3], 40],
              [[2500, 45000], [1, 2, 3], 80], [[20000, 15000], [1, 2, 3], 80]]
    Obstacles = []
    for i in range(len(airport)):
        c_air = population_generation.Airport(i + 1, airport[i][0], airport[i][1], airport[i][2])
        airports.append(c_air)
    for i in range(len(target)):
        c_tar = population_generation.Target(i + 1, target[i][0], target[i][1], target[i][2])
        targets.append(c_tar)
    for i in range(len(Uav)):
        c_uav = population_generation.UAV(i + 1, Uav[i][0], Uav[i][1], Uav[i][2], Uav[i][3], Uav[i][4], airports)
        uavs.append(c_uav)
    for obstacle in obstacles:
        if obstacle[0] == 1:
            Obs = MAP.Obstacle('o', obstacle[1])
        else:
            Obs = MAP.Obstacle('p', obstacle[1])
        Obstacles.append(Obs)
    current_iter = 1
    max_iter = 20
    tea_num = 4
    solutions, _ = population_generation.coding_population(targets, uavs, 10)
    new_solutions = population_update(current_iter, max_iter, solutions, uavs, targets, Obstacles)
    print('交叉得到的种群是', new_solutions)
