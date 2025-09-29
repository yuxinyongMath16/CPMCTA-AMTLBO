# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2022年11月07日
daswoa算法中的染色体种群更新操作，包含单点交叉，以及各种概率计算
"""
import random
import population_generation
import math
import MAP
import numpy as np
import copy


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


# 计算参数A，C
def calculate_parameter(current_iter, max_iter):
    a = 2 - 2 * (current_iter / max_iter)
    gama1 = random.random()
    gama2 = random.random()
    parameter_a = 2 * a * gama1 - a
    parameter_c = 2 * a * gama2
    return parameter_a, parameter_c


# 计算参数，大写gama和大写L
def calculate_population_dispersion_degree(solution_fit_set, current_iter, max_iter):
    population_size = len(solution_fit_set)
    fitness = []
    for solution_fit in solution_fit_set:
        fitness.append(solution_fit[1])
    f_ave = np.mean(fitness)
    differential_value = []
    max_value = 0
    for i in range(len(fitness)):
        differential = abs(fitness[i] - f_ave)
        differential_value.append(differential)
        if differential > max_value:
            max_value = differential
    population_degree = 0
    for i in range(len(differential_value)):
        population_degree += differential_value[i]/max_value
    population_degree = math.sqrt(population_degree/population_size)
    capital_gamma = 0.5*math.log2(2-population_degree) + 0.5*(1-current_iter/max_iter)
    capital_l = 0.5*math.log2(population_degree+1)+0.5*current_iter/max_iter
    return capital_gamma, capital_l


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
    new_solution = sorted(new_solution, key=(lambda x: x[2]))
    # print('排序后,解的编码', new_solution)
    return new_solution, new_resource


def calculate_parameter_d_b(f_best, f_worst, f_xi):
    return abs(f_best - f_xi) / (f_best - f_worst)


def calculate_parameter_d_e(f_best, f_worst, f_xi, parameter_c):
    return abs(parameter_c * f_best - f_xi) / (f_best - f_worst)


def calculate_parameter_d_s(f_best, f_worst, f_xi, f_rand, parameter_c):
    return abs(parameter_c * f_rand - f_xi) / (f_best - f_worst)


# 领导者选择，从最小值中选择，solution_fit_set是从小到大
def exploitation_phase_leader_select(solution_fit_set, select_parameter, sorted_index, resources):
    # print('选择领导者，看一下排序集合', solution_fit_set)
    exploitation_leader = []
    exploitation_leader_resources = []
    population_size = len(solution_fit_set)
    ncl = int(population_size*select_parameter)
    # print('选择', ncl, '个精英')
    for i in range(ncl):
        exploitation_leader.append(solution_fit_set[i][0])
        # print('选择精英的最优值是', solution_fit_set[i][1])
        exploitation_leader_resources.append(resources[sorted_index[i]])
    return exploitation_leader, exploitation_leader_resources


def roulette(pjl_set):
    # 第一步、计算所有无人机被选择的概率
    # 第二步、计算染色体概率，即将所有适应度归一化
    res_probability = []
    for ammo in pjl_set:
        probability = ammo / sum(pjl_set)
        res_probability.append(probability)
    # 第三步、计算累计概率
    cum_probability = [0]
    for i in range(len(res_probability)):
        cum = 0
        for j in range(i + 1):
            cum = cum + res_probability[j]
        cum_probability.append(cum)
    # print('累计概率', cum_probability)
    # 第四步、产生随机数，选择个体
    rand = random.random()
    # print('产生的随机数', rand)
    for p in range(len(cum_probability) - 1):
        if cum_probability[p] < rand <= cum_probability[p + 1]:
            rand_number = p
    return rand_number


def exploration_phase_leader_select(solution_fit_set, select_parameter, xi, sorted_index, resources):
    # set是方案+解形式的集合
    exploration_leader_set = []
    population_size = len(solution_fit_set)
    ncl = int(population_size * select_parameter)
    rand_num2 = random.randint(0, len(solution_fit_set) - 1)
    exploration_leader_set.append(solution_fit_set[rand_num2])
    exploration_leader = [solution_fit_set[rand_num2][0]]
    # 增加资源集合
    exploration_leader_resources = [resources[sorted_index[rand_num2]]]
    exploration_leader_judge = [xi, rand_num2]
    max_zeta = 0
    zeta = []
    for i in range(len(solution_fit_set)):
        zeta_value = abs(solution_fit_set[i][1]-solution_fit_set[xi][1])
        for j in range(len(exploration_leader_set)):
            zeta_value += abs(solution_fit_set[i][1]-exploration_leader_set[j][1])
        zeta.append(zeta_value/(1+len(exploration_leader_set)))
        if zeta[-1] > max_zeta:
            max_zeta = zeta[-1]
    pjl_set = []
    for i in range(len(zeta)):
        pjl = zeta[i]/max_zeta
        pjl_set.append(pjl)
    # print('概率集的长度', len(pjl_set), '种群的长度', len(solution_fit_set))
    while len(exploration_leader) < ncl:
        rand_num = roulette(pjl_set)
        if rand_num not in exploration_leader_judge:
            exploration_leader_judge.append(rand_num)
            # print('为什么会超出范围', solution_fit_set[rand_num])
            exploration_leader.append(solution_fit_set[rand_num][0])
            exploration_leader_resources.append(resources[sorted_index[rand_num]])
    return exploration_leader, exploration_leader_resources


def population_update(current_iter, max_iter, solutions, resources, uavs, targets, Obstacles, threat_r):
    b = 0.95
    select_parameter = 0.06
    new_solutions = []
    new_resources = []
    solution_fit_set, sorted_index = population_generation.sorting_solution(solutions, targets, uavs, Obstacles, threat_r)
    population_size = len(solution_fit_set)
    exploitation_leader, exploitation_leader_resources = exploitation_phase_leader_select(solution_fit_set,
                                                                                          select_parameter,
                                                                                          sorted_index, resources)

    for i in range(len(exploitation_leader)):
        new_solutions.append(exploitation_leader[i])
        new_resources.append(exploitation_leader_resources[i])
    # print('迭代前此代最优精英', new_solutions[0])
    for i in range(population_size - len(exploitation_leader)):
        if len(new_solutions) == population_size:
            break
        capital_gamma, capital_l = calculate_population_dispersion_degree(solution_fit_set, current_iter, max_iter)
        parameter_a, parameter_c = calculate_parameter(current_iter, max_iter)
        # print('四个参数计算为：', capital_gamma, capital_l, parameter_a, parameter_c)
        rho = random.random()
        # print('随机数rho为', rho)
        if rho <= capital_gamma:
            # print('开发阶段领导者', exploitation_leader)
            for j in range(len(exploitation_leader)):
                if abs(parameter_a) < capital_l:
                    d_e = calculate_parameter_d_e(solution_fit_set[0][1], solution_fit_set[-1][1], solution_fit_set[i][1],
                                                  parameter_c)
                    h_xi = parameter_a * d_e / 2
                else:
                    d_b = calculate_parameter_d_b(solution_fit_set[0][1], solution_fit_set[-1][1], solution_fit_set[i][1])
                    parameter_l = random.random() * 2 - 1
                    h_xi = abs(d_b * math.exp(parameter_l * b) * math.cos(2 * math.pi * parameter_l))
                if h_xi < 0.5:
                    # print('进行一次单点交叉')
                    new_solution, new_resource = single_point_crossover(exploitation_leader[j], solution_fit_set[i][0], uavs,
                                                             targets)
                    new_solutions.append(new_solution)
                    new_resources.append(new_resource)
                    if len(new_solutions) == population_size:
                        break
                else:
                    # print('进行两次单点交叉')
                    new_solution1, _ = single_point_crossover(exploitation_leader[j], solution_fit_set[i][0], uavs,
                                                              targets)
                    new_solution, new_resource = single_point_crossover(exploitation_leader[j], new_solution1, uavs, targets)
                    new_solutions.append(new_solution)
                    new_resources.append(new_resource)
                    if len(new_solutions) == population_size:
                        break
        else:
            exploration_leader, _ = exploration_phase_leader_select(solution_fit_set, select_parameter, i, sorted_index, resources)
            # print('探索阶段领导者', exploration_leader)
            for j in range(len(exploration_leader)):
                rand_num = random.randint(0, len(solution_fit_set) - 1)
                d_s = calculate_parameter_d_s(solution_fit_set[0][1], solution_fit_set[-1][1], solution_fit_set[i][1],
                                              solution_fit_set[rand_num][1], parameter_c)
                h_xi = parameter_a * d_s / 2
                if h_xi < 0.5:
                    # print('进行一次单点交叉')
                    new_solution, new_resource = single_point_crossover(exploration_leader[j], solution_fit_set[i][0], uavs, targets)
                    new_solutions.append(new_solution)
                    new_resources.append(new_resource)
                    if len(new_solutions) == population_size:
                        break
                else:
                    # print('进行两次单点交叉')
                    new_solution1, _ = single_point_crossover(exploration_leader[j], solution_fit_set[i][0], uavs, targets)
                    new_solution, new_resource = single_point_crossover(exploration_leader[j], new_solution1, uavs, targets)
                    new_solutions.append(new_solution)
                    new_resources.append(new_resource)
                    if len(new_solutions) == population_size:
                        break
    # print('迭代后此代最优精英', new_solutions[0])
    # print('新的种群长度', len(new_solutions))
    # print('新种群', new_solutions)
    # print('资源约束集', new_resources)
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
    current_iter = 10
    max_iter = 20
    solutions, resources = population_generation.coding_population(targets, uavs, Obstacles, 10)
    new_solutions, new_resources = population_update(current_iter, max_iter, solutions, resources, uavs, targets, Obstacles)
    print('交叉得到的种群是', new_solutions)
