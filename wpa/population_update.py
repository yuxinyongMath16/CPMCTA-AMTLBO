# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2023年07月24日
wpa任务分配算法种群更新
"""

import copy
import random
import population_generation
import math
import MAP
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


# 精英种群生成
def elite_population_generation(solutions, fitness, resources, n_star):
    elite_population = []
    # print('适应度函数', fitness)
    sort_fitness = np.argsort(fitness)
    elite_resources = []
    sort_population = []
    sort_resources = []
    # print('初始种群是', solutions)
    # print('初始的资源集合', resources)
    # print('适应度排序结果是', sort_fitness)
    for i in range(len(solutions)):
        if i < n_star:
            elite_population.append(solutions[sort_fitness[i]])
            elite_resources.append(resources[sort_fitness[i]])
        sort_population.append(solutions[sort_fitness[i]])
        sort_resources.append(resources[sort_fitness[i]])
    # print('精英数量', n_star)
    # print('精英种群', elite_population)
    # print('精英资源约束集', elite_resources)
    # print('种群排序集合', sort_population)
    # print('资源排序集合', sort_resources)
    return elite_population, elite_resources, sort_population, sort_resources


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
def mutation(chromosome, resource, PM = 1):
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


def safari_process(elite_population, elite_resources):
    new_population = [elite_population[0]]
    new_resources = [elite_resources[0]]
    for i in range(len(elite_population)-1):
        m_chromosome, m_resource = mutation(elite_population[i+1], elite_resources[i+1])
        new_population.append(m_chromosome)
        new_resources.append(m_resource)
    return new_population, new_resources


def close_to_best_wolf_process(sort_population, n_star, uavs, targets):
    new_population = []
    new_resources = []
    best_solution = sort_population[0]
    for i in range(len(sort_population)-n_star):
        new_solution, new_resource = single_point_crossover(sort_population[i+n_star], best_solution, uavs, targets)
        new_population.append(new_solution)
        new_resources.append(new_resource)
    return new_population, new_resources


def population_update(solutions, resources, fitness, n_star, targets, uavs):
    # 一、生成精英种群和排序种群
    elite_population, elite_resources, sort_population, sort_resources = elite_population_generation(solutions, fitness, resources, n_star)
    # 二、探狼游走
    new_elite_population, new_elite_resources = safari_process(elite_population, elite_resources)
    # 三、猛狼呼唤
    new_wolf_solutions, new_wolf_resources = close_to_best_wolf_process(sort_population, n_star, uavs, targets)
    # 四、组合种群，生成新的一代
    new_populations = copy.deepcopy(new_elite_population) + copy.deepcopy(new_wolf_solutions)
    # print('新种群大小', len(new_populations))
    # new_resources = copy.deepcopy(new_elite_resources) + copy.deepcopy(new_wolf_resources)
    # for i in range(len(new_wolf_solutions)):
    #     new_populations.append(new_wolf_solutions[i])
    #     new_resources.append(new_wolf_resources[i])
    return new_populations


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
    solutions, _ = population_generation.coding_population(targets, uavs, 10)
    new_solutions = population_update(current_iter, max_iter, solutions, uavs, targets, Obstacles)
    print('交叉得到的种群是', new_solutions)
