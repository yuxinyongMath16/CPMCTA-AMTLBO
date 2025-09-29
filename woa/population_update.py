# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2022年11月08日
离散鲸鱼优化算法（dwoa）的迭代方式
"""
import copy
import random
import population_generation
import math
import MAP


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


def calculate_parameter_d_b(f_best, f_worst, f_xi):
    if f_best - f_worst == 0:
        return abs(f_best - f_xi) / 0.01
    else:
        return abs(f_best - f_xi) / (f_best - f_worst)


def calculate_parameter_d_e(f_best, f_worst, f_xi, parameter_c):
    if f_best - f_worst == 0:
        return abs(parameter_c * f_best - f_xi) / 0.01
    else:
        return abs(parameter_c * f_best - f_xi) / (f_best - f_worst)


def calculate_parameter_d_s(f_best, f_worst, f_xi, f_rand, parameter_c):
    if f_best - f_worst == 0:
        return abs(parameter_c * f_rand - f_xi) / 0.01
    else:
        return abs(parameter_c * f_rand - f_xi) / (f_best - f_worst)


def population_update(current_iter, max_iter, solutions, uavs, targets, Obstacles, threat_r):
    b = 0.95
    new_solutions = []
    solution_fit_set = population_generation.sorting_solution(solutions, targets, uavs, Obstacles, threat_r)
    # print('解序列排序', solution_fit_set)
    new_solutions.append(copy.deepcopy(solution_fit_set[0][0]))
    # print('添加第一个解后的新解序列', new_solutions)
    for i in range(len(solution_fit_set) - 1):
        parameter_a, parameter_c = calculate_parameter(current_iter, max_iter)
        if parameter_a <= 1:
            rand_num1 = random.random()
            if rand_num1 <= 0.5:
                d_e = calculate_parameter_d_e(solution_fit_set[-1][1], solution_fit_set[0][1], solution_fit_set[i][1],
                                              parameter_c)
                h_xi = parameter_a * d_e / 2
            else:
                d_b = calculate_parameter_d_b(solution_fit_set[-1][1], solution_fit_set[0][1], solution_fit_set[i][1])
                parameter_l = random.random() * 2 - 1
                h_xi = abs(d_b * math.exp(parameter_l * b) * math.cos(2 * math.pi * parameter_l))
        else:
            rand_num2 = random.randint(0, len(solution_fit_set) - 1)
            d_s = calculate_parameter_d_s(solution_fit_set[-1][1], solution_fit_set[0][1], solution_fit_set[i][1],
                                          solution_fit_set[rand_num2][1], parameter_c)
            h_xi = parameter_a * d_s / 2
        if h_xi <= 0.5:
            # print('进行一次单点交叉')
            new_solution, _ = single_point_crossover(solution_fit_set[0][0], solution_fit_set[i][0], uavs, targets)
            new_solutions.append(new_solution)
            # print('添加新解后的新解序列', new_solutions)
        else:
            # print('进行两次单点交叉')
            new_solution1, _ = single_point_crossover(solution_fit_set[0][0], solution_fit_set[i][0], uavs, targets)
            new_solution, _ = single_point_crossover(solution_fit_set[0][0], new_solution1, uavs, targets)
            new_solutions.append(new_solution)
            # print('添加新解后的新解序列', new_solutions)
    # new_solution_fit_set = population_generation.sorting_solution(new_solutions, targets, uavs, Obstacles)
    # print('新的种群解序列排序', new_solution_fit_set)
    # print('新种群长度：', len(new_solutions))
    # print('新种群排序长度', len(new_solution_fit_set))
    # print('新种群第一个解', new_solutions[0])
    return new_solutions


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
