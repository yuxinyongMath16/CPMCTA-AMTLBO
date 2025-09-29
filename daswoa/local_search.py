# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2022年11月09日
daswoa局部搜机制，即变异机制
"""

import copy
import random
import population_update
import population_generation
import math
import MAP


def attack_exchange(solution, resource, num):
    iteration = 0
    while True:
        random_num = random.randint(0, len(resource[1]) - 1)
        if resource[1][random_num] != solution[num][2] and resource[2][random_num] > 0:
            exchange_uav_num = resource[1][random_num]
            resource = population_update.resource_update(resource, solution[num][2], 1, 1)
            solution[num][2] = exchange_uav_num
            resource = population_update.resource_update(resource, exchange_uav_num, 1, 0)
            break
        iteration += 1
        if iteration > 20:
            break
    return solution, resource


def detect_exchange(solution, resource, num):
    while True:
        random_num = random.randint(0, len(resource[0]) - 1)
        if resource[0][random_num] != solution[num][2]:
            solution[num][2] = resource[0][random_num]
            break
    # exchange_uav_num = resource[0][random_num]
    # solution[num][2] = exchange_uav_num
    return solution, resource


def change_uav_num(solution, resource, num):
    if solution[num][1] == 2:
        solution, resource = attack_exchange(solution, resource, num)
    else:
        solution, resource = detect_exchange(solution, resource, num)
    return solution, resource


# 变异函数
def mutation(solution, resource):
    m_solution = copy.deepcopy(solution)
    m_resource = copy.deepcopy(resource)
    rand_mutation = random.random()
    # 一、对该染色体执行对随机目标改变执行无人机
    if rand_mutation < 0.5:
        # print('对该染色体执行对随机目标改变执行无人机')
        # print('执行改变随机任务执行UAV编号的变异')
        random_num1 = random.randint(0, len(m_solution) - 1)
        # print('改变随机任务执行UAV编号前', m_chromosome)
        # print('变异前的染色体', m_solution)
        # print('变异前的资源约束集', m_resource)
        # print('变异位置', random_num1)
        m_solution, m_resource = change_uav_num(m_solution, m_resource, random_num1)
        # print('改变随机任务执行UAV编号后', m_chromosome)
        m_solution = sorted(m_solution, key=(lambda x: x[2]))
        # print('变异后的染色体', m_solution)
        # print('变异后的资源约束集', m_resource)
    # 二、 改变随机选择的无人机的任务顺序
    else:
        # print('改变随机选择的无人机的任务顺序')
        random_num2 = random.randint(0, len(m_solution) - 1)
        while True:
            random_num3 = random.randint(0, len(m_solution) - 1)
            if random_num2 != random_num3:
                break
        # print('变异前的染色体', m_solution)
        # print('交换的列', random_num2, random_num3)
        storage_column = copy.deepcopy(m_solution[random_num2])
        m_solution[random_num2] = m_solution[random_num3]
        m_solution[random_num3] = storage_column
        # print('变异后的染色体，未排序', m_solution)
        m_solution = sorted(m_solution, key=(lambda x: x[2]))
        # print('变异后的染色体，排序', m_solution)
    return m_solution, m_resource


def local_search(solutions, resources, elite_num):
    new_solutions = []
    new_resources = []
    for i in range(len(solutions)):
        if i < elite_num:
            new_solutions.append(solutions[i])
            new_resources.append(resources[i])
        else:
            m_solution, m_resource = mutation(solutions[i-elite_num], resources[i-elite_num])
            new_solutions.append(m_solution)
            new_resources.append(m_resource)
    # print('变异的染色体是', new_solutions)
    # print('变异后的资源约束集', new_resources)
    return new_solutions, new_resources


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
    solutions, resources = population_generation.coding_population(targets, uavs, Obstacles, 10)
    new_solutions, new_resources = local_search(solutions, resources)
    print('变异的染色体是', new_solutions)
    print('变异后的资源约束集', new_resources)
