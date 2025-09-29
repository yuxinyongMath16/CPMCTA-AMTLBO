# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2022年06月01日
"""
import random
import copy
import chromosome_generation
import unlock


# 轮盘赌选择交叉亲本
def roulette(fitness):
    # 第一步、计算所有染色体适应度
    # 第二步、计算染色体概率，即将所有适应度归一化
    fit_probability = []
    for fit in fitness:
        probability = fit / sum(fitness)
        fit_probability.append(probability)
    # 第三步、计算累计概率
    cum_probability = [0]
    for i in range(len(fit_probability)):
        cum = 0
        for j in range(i + 1):
            cum = cum + fit_probability[j]
        cum_probability.append(cum)
    # 第四步、产生随机数，选择个体
    rand1 = random.random()
    for p in range(len(cum_probability) - 1):
        if cum_probability[p] < rand1 <= cum_probability[p + 1]:
            rand_number1 = p
    while True:
        rand2 = random.random()
        for p in range(len(cum_probability) - 1):
            if cum_probability[p] < rand2 <= cum_probability[p + 1]:
                rand_number2 = p
        if rand_number1 != rand_number2:
            break
    return rand_number1, rand_number2


# 资源更新函数,update_type = 1弹药增加，update_type = 0 弹药减少,资源集合，编号，弹药数量，类型
def resource_update(resource, num, ammo_num, update_type):
    if update_type == 0:
        resource[2][num - 1] = resource[2][num - 1] - ammo_num
        if resource[2][num - 1] == 0:
            resource[1].remove(num)
    else:
        if num not in resource[1]:
            resource[1].append(num)
        resource[2][num - 1] = resource[2][num - 1] + ammo_num
    return resource


# 计算亲本的可执行攻击任务的集合，资源约束集除去所有执行对该目标进行过攻击任务的无人机， 染色体，染色体攻击无人机集合，变异的染色体列数
def remainder_attack_calculation(c_chromosome, c_resourceAtt, location):
    chrom_att = []
    remainder_attack = []
    #
    for i in range(len(c_chromosome)):
        if c_chromosome[i][0] == c_chromosome[location][0] and c_chromosome[i][1] == 2:
            chrom_att.append(c_chromosome[i][2])
    for i in range(len(c_resourceAtt)):
        # print('打印i和攻击集合', i, c_resourceAtt, chrom_att)
        if c_resourceAtt[i] not in chrom_att:
            remainder_attack.append(c_resourceAtt[i])
    return remainder_attack


# 交叉算法
def crossover(chromosomes, resources, fitness):
    # 第一步、通过转轮赌方法随机选择进行交叉操作的亲本
    rand_num1, rand_num2 = roulette(fitness)
    angle_record1 = []
    angle_record2 = []
    '''染色体是否进行修改，只需要修改此地方即可'''
    c_chromosome1 = copy.deepcopy(chromosomes[rand_num1])
    c_chromosome2 = copy.deepcopy(chromosomes[rand_num2])
    c_resource1 = copy.deepcopy(resources[rand_num1])
    c_resource2 = copy.deepcopy(resources[rand_num2])
    # print('交叉前的两个染色体', c_chromosome1, c_chromosome2)
    # 第二步、随机选择亲本1的某一点为单点交叉的起始点
    chromosome_num = len(c_chromosome1)
    start_point = random.randint(0, chromosome_num - 1)

    # 第三步，开始单点交叉，通过if判断语句对于三种不同任务类型的任务进行对应的交叉操作
    for i in range(chromosome_num-start_point):
        if c_chromosome1[i+start_point][1] == 2:
            # （1）将第二个染色体的攻击任务都找出来
            attack_list2 = []
            for p in range(len(c_chromosome2)):
                if c_chromosome2[p][1] == 2:
                    attack_list2.append([c_chromosome2[p][2], p])  # attack_list2 = [[执行攻击任务无人机编号，染色体列数],...]

            # （2）资源约束集除去执行第一个亲本此DNA的无人机编号，，的所有所有所有无人机
            remainder_attack = remainder_attack_calculation(c_chromosome1, c_resource1[1], i + start_point)

            # （3）计算交集（第一个染色体可进行攻击的(除去被选中进行交叉的uav)交 第二个染色体执行攻击的uav），随机算出第二个亲本染色体进行交叉的DNA片段
            # 交集交的不彻底。。。。。
            attack_inter = []
            for q in range(len(remainder_attack)):
                for r in range(len(attack_list2)):
                    if remainder_attack[q] == attack_list2[r][0]:  # 交集就是大家都有的元素
                        attack_inter.append(attack_list2[r])
            if len(attack_inter) != 0:  # 交集不为空，才可进行交叉操作。且分为两种情况，一是满足资源约束集，二是不满足资源约束集
                rand_attack2 = random.randint(0, len(attack_inter) - 1)
                crossover_num2 = attack_inter[rand_attack2][1]  # 确定第二个染色体进行交叉的列
                # 记录无人机编号，用于更改资源约束集, 可能会引起错误，删除
                # uav_num = [c_chromosome1[i + start_point][2], c_chromosome2[crossover_num2][2]]

                # （4）两个DNA片段交换，攻击基因交换完毕。此处需要分情况考虑，因为会出现第二个染色体不满足弹药约束的情况。而且需要更新资源约束集
                # 进行交叉的两个片段是染色体1的 i+start_point 列 和 染色体2的 crossover_num2列

                storage_chromosome = []  # 这个向量需要换入亲本2中
                s_constraint = 0  # 用于判断是否满足资源约束
                #
                # # 计算染色体2中对于交叉行目标攻击的无人机，
                # chrom_att2 = []
                # for l in range(len(c_chromosome2)):
                #     if c_chromosome2[l][0] == c_chromosome2[crossover_num2][0] and c_chromosome2[l][1] == 2:
                #         chrom_att2.append(c_chromosome2[l][2])
                #
                # s_constraint = 1 表示资源支持这次交换
                for l in range(len(c_resource2[1])):
                    if c_resource2[1][l] == c_chromosome1[i + start_point][2] and c_resource2[2][c_chromosome1[i + start_point][2]-1] != 0:
                        s_constraint = 1
                #
                # # 如果第二个染色体交叉过程中满足资源约束，直接进行交叉
                if s_constraint == 1:
                    # if c_chromosome2[crossover_num2][2] not in chrom_att2:
                    storage_chromosome.append(c_chromosome1[i + start_point][2])
                    c_chromosome1[i + start_point][2] = copy.deepcopy(c_chromosome2[crossover_num2][2])
                    c_chromosome2[crossover_num2][2] = copy.deepcopy(storage_chromosome[0])
                    # 染色体2资源约束集更新，亲本1部分，需要删去部分（被选中部分）
                    c_resource2 = resource_update(c_resource2, c_chromosome1[i + start_point][2], 1, 1)
                    c_resource2 = resource_update(c_resource2, c_chromosome2[crossover_num2][2], 1, 0)
                    # 染色体1资源约束集更新，亲本1,2部分，需要删去和加入部分
                    c_resource1 = resource_update(c_resource1, c_chromosome2[crossover_num2][2], 1, 1)
                    c_resource1 = resource_update(c_resource1, c_chromosome1[i + start_point][2], 1, 0)
                    # print('攻击基因交叉完成')
        else:  # 如果是侦查或者评估基因则用下面的方法进行交叉
            # （1）将第二个染色体的侦查评估任务都找出来
            detect_list2 = []
            # print('侦查评估任务执行前的染色体1%%%%%%%%%%%%%%：',c_chromosome1)
            # print('侦查评估任务执行前的染色体2%%%%%%%%%%%%%%：',c_chromosome2)
            for p in range(len(c_chromosome2)):
                if c_chromosome2[p][1] != 2:
                    detect_list2.append([c_chromosome2[p][2], p])

            # （2）资源约束集除去执行第一个亲本此DNA的无人机编号
            remainder_detect = []
            for decuav in c_resource1[0]:
                if decuav != c_chromosome1[i + start_point][2]:
                    remainder_detect.append(decuav)

            # （3）计算交集，随机算出第二个亲本染色体进行交叉的DNA片段
            detect_inter = []
            for q in range(len(remainder_detect)):
                for j in range(len(detect_list2)):
                    if remainder_detect[q] == detect_list2[j][0]:
                        detect_inter.append(detect_list2[j])
            if len(detect_inter) != 0:

                rand_detect2 = random.randint(0, len(detect_inter) - 1)
                crossover_num2 = detect_inter[rand_detect2][1]

                # （4）两个DNA片段交换，侦查评估基因交换完毕
                storage_chromosome = []
                for j in range(1):
                    storage_chromosome.append(c_chromosome1[i + start_point][j + 2])
                    c_chromosome1[i + start_point][j + 2] = copy.deepcopy(c_chromosome2[crossover_num2][j + 2])
                    c_chromosome2[crossover_num2][j + 2] = copy.deepcopy(storage_chromosome[j])
    # 第四步，将染色体根据无人机编号顺序重新排列
    # print('交叉后没有排序的染色体', c_chromosome1, c_chromosome2)
    c_chromosome1 = sorted(c_chromosome1, key=(lambda x: x[2]))
    c_chromosome2 = sorted(c_chromosome2, key=(lambda x: x[2]))
    # print('交叉后排序的染色体', c_chromosome1, c_chromosome2)
    return c_chromosome1, c_chromosome2, c_resource1, c_resource2


def main(targets, uavs, Obstacles, population):
    chromosomes, resources = chromosome_generation.codingChromosome(targets, uavs, population)
    fitness = unlock.fitness(chromosomes, targets, uavs, Obstacles)
    new_chromosomes = []
    new_resources = []
    for i in range(4):
        c_chromosome1, c_chromosome2, c_resource1, c_resource2 = crossover(chromosomes, resources, fitness)
        new_chromosomes.append(c_chromosome1)
        new_chromosomes.append(c_chromosome2)
        new_resources.append(c_resource1)
        new_resources.append(c_resource2)
        # print('已进行交叉次数：&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&',i)
    chromosomes = new_chromosomes
    resources = new_resources
    print('交叉的染色体是', chromosomes)
    print('交叉后的资源约束集', resources)


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
    main(targets, uavs, Obstacles, 10)
