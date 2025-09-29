# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2022年06月01日
"""
import copy
import random
import crossover
import chromosome_generation
import unlock


def attack_exchange(chromosome, resource, num):
    random_num = random.randint(0, len(resource[1]) - 1)
    exchange_uav_num = resource[1][random_num]
    resource = crossover.resource_update(resource, chromosome[num][2], 1, 1)
    chromosome[num][2] = exchange_uav_num
    resource = crossover.resource_update(resource, exchange_uav_num, 1, 0)
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
        chromosome,resource = detect_exchange(chromosome, resource, num)
    return chromosome,resource


# 变异函数
def mutation(chromosomes, resources, PM = 0.5):
    DNA_num = random.randint(0, len(chromosomes) - 1)
    m_chromosome = copy.deepcopy(chromosomes[DNA_num])
    m_resource = copy.deepcopy(resources[DNA_num])
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


def main(targets, uavs, population):
    chromosomes, resources = chromosome_generation.codingChromosome(targets, uavs, population)
    new_chromosomes = []
    new_resources = []
    for i in range(4):
        m_chromosome, m_resource = mutation(chromosomes, resources)
        new_chromosomes.append(m_chromosome)
        new_resources.append(m_resource)
        # print('已进行交叉次数：&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&',i)
    chromosomes = new_chromosomes
    resources = new_resources
    print('变异的染色体是', chromosomes)
    print('变异后的资源约束集', resources)

if __name__ == '__main__':
    airport = [[[800, 0], 2], [[-2000, 2000], 0]]
    Uav = [[[800, 0], 1, 80, 0, 250], [[800, 0], 3, 60, 5, 220], [[800, 0], 2, 70, 2, 200]]
    target1 = [[[2200, 4000], [1, 2, 3], 60], [[3200, 1700], [1, 2, 3], 90], [[1700, 1700], [1, 2, 3], 90]]
    target = [[[2200, 4000], [1, 2, 3], 60], [[1700, 1700], [1, 2, 3], 90]]
    targets = []
    uavs = []
    Obstacles = []
    for i in range(len(target)):
        c_tar = chromosome_generation.Target(i + 1, target[i][0], target[i][1], target[i][2])
        targets.append(c_tar)
    for i in range(len(Uav)):
        c_uav = chromosome_generation.UAV(i + 1, Uav[i][0], Uav[i][1], Uav[i][2], Uav[i][3], Uav[i][4])
        uavs.append(c_uav)
    main(targets, uavs, 10)