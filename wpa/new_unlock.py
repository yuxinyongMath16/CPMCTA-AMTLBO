#coding:utf-8
import numpy as np
import matplotlib.pyplot as plt
import random
import math
import copy
import time


#一个常用的模块
'''
对一个无人机的剩余所有任务使用，遍历执行
1、遇到1加入C，C_S
2、遇到2判断编号是否在C_S中
更新相应集合ab，delete ，C_S，A，can_V，A_P
3、遇到3判断编号是否在can_V中
更新相应集合 ab，delete ，V
'''


def traversexecution(Pro_uav,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,i):
    zhixingshu = 0
    # print('输入的子方案：',Pro_uav)
    #print('执行操作的染色体：',Pro_uav)
    for j in range(len(Pro_uav)):
        if Pro_uav[j][1] == 1:
            # print('执行侦查任务')
            Detect.append(Pro_uav[j][0])
            Detect_S.append(Pro_uav[j][0])
            zhixingshu = zhixingshu + 1
        elif Pro_uav[j][1] == 2:
            if Pro_uav[j][0] in Detect_S:
                # print('执行攻击任务')
                # print('被删减集合：',Attack_position[Pro_uav[j][0]-1],'删减集：',[i,j])
                Attack_num[Pro_uav[j][0]-1] = Attack_num[Pro_uav[j][0]-1] + 1
                Attack_position[Pro_uav[j][0]-1].remove([i,j])
                if Attack_num[Pro_uav[j][0]-1] == program_attack[Pro_uav[j][0]-1]:
                    Can_evaluate[Pro_uav[j][0]-1] = 1
                    Detect_S.remove(Pro_uav[j][0])
                zhixingshu = zhixingshu + 1
            else:
                break
        elif Pro_uav[j][1] == 3:
            if Can_evaluate[Pro_uav[j][0]-1] == 1:
                # print('执行评估任务')
                Evaluation[Pro_uav[j][0]-1] = 1
                zhixingshu = zhixingshu + 1
            else:
                break
    #删除已经执行的列
    for j in range(len(Pro_uav)):
        if j+1 <= zhixingshu:
            Pro_uav.pop(zhixingshu-j-1)
        else:
            break
    Executed[i] = Executed[i] + zhixingshu
    #当执行数大于0时，更新攻击任务位置集合
    if zhixingshu > 0:
        for j in range(len(Pro_uav)):
            if Pro_uav[j][1] == 2:
                for p in range(len(Attack_position[Pro_uav[j][0]-1])):
                    if Attack_position[Pro_uav[j][0]-1][p][0] == i and Attack_position[Pro_uav[j][0]-1][p][1] == j + zhixingshu:
                        # print('需要更新的集合',Attack_position[Pro_uav[j][0]-1],'子方案编号：',i,'子方案执行数：',zhixingshu,'被执行任务：',Attack_position[Pro_uav[j][0]-1][p])
                        Attack_position[Pro_uav[j][0]-1][p][1] = Attack_position[Pro_uav[j][0]-1][p][1] - zhixingshu
    
    # print('输出的子方案：',Pro_uav)
    return Pro_uav,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack

#解锁策略1
'''
遇到能执行的任务就往下执行，直至被锁（用于初始化）
'''
def unlockStrategy1(Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack):
    #只要有一个子维度发生变化，整个方案就是还没有被锁死
    Plandim_jugement = 0
    subdim_jugement = 0

    for i in range(len(Program)):
        be_subdim = len(Program[i])
        if len(Program[i]) != 0:
            Program[i],Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack = traversexecution(Program[i],Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,i)
        af_subdim = len(Program[i])
        
        # 如果子维度发生改变，则将判断条件改变
        if be_subdim != af_subdim:
            subdim_jugement = 1
    # 如果所有子维度都没有发生改变，则说明锁死
    if subdim_jugement == 0:
        Plandim_jugement = 1
    return Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,Plandim_jugement

#解锁策略2(涉及换序)
'''
C_S为空集，C的势小于任务数时执行

寻找1，找到就换出
'''
def unlockStrategy2(Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,unlock_set):
    find = 0 #寻找1，找到交换完就退出
    start_point = 0
    for i in range(len(Program)):
        for j in range(len(Program[i])):
            if Program[i][j][1] == 1:
                storage = copy.deepcopy(Program[i][0])
                Program[i][0] = copy.deepcopy(Program[i][j])
                Program[i][j] = copy.deepcopy(storage)
                unlock_set.append([i,0+Executed[i],j+Executed[i]])   # 解锁方案集合[第几个DNA，DNA中互换的第一个位置，DNA中互换的第二个位置]
                # 更新攻击位置集合
                # print('换前位置：',Attack_position,'两个位置为：',i,j)
                Attack_position = upgradeAttackposition(Program,i,j,Attack_position)
                # print('换后位置：',Attack_position)
                find = 1
                start_point = i
                break
        if find == 1:
            break
    for i in range(len(Program)-start_point):
        if len(Program[i+start_point]) != 0:
            Program[i+start_point],Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack = traversexecution(Program[i+start_point],Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,i+start_point)
                
    return Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,unlock_set

#解锁策略3(涉及换序)
'''
C_S不为空集时执行

找第一个元素的攻击无人机，进行换序，换序后更新 unlock_set
'''
def unlockStrategy3(Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,unlock_set):
    exchange_att = Detect_S[0]
    position1 = Attack_position[exchange_att-1][0][0]
    position2 = Attack_position[exchange_att-1][0][1]
    storage = copy.deepcopy(Program[position1][0])
    Program[position1][0] = copy.deepcopy(Program[position1][position2])
    Program[position1][position2] = copy.deepcopy(storage)
    unlock_set.append([position1,0+Executed[position1],position2+Executed[position1]])     # 解锁方案集合[第几个DNA，DNA中互换的第一个位置，DNA中互换的第二个位置]
    # 更新攻击位置集合
    # print('换前位置：',Attack_position,'两个位置为：',position1,position2)
    Attack_position = upgradeAttackposition(Program,position1,position2,Attack_position)
    # print('换后位置：',Attack_position)
    for i in range(len(Program)-position1):
        if len(Program[i+position1]) != 0:
            Program[i+position1],Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack = traversexecution(Program[i+position1],Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,i+position1)
    return Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,unlock_set


#解锁策略4(涉及换序)
'''
C_S为空集，C的势等于任务数时执行

遍历can_V，如果有未完成的攻击任务，找到位置换出（涉及换序）
并且从换序的染色体往后执行一遍
'''
def unlockStrategy4(Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,target_s,unlock_set):
    exchange_att = 0
    for i in range(len(Can_evaluate)):
        if Can_evaluate[i] == 0 and i+1 in target_s:
            exchange_att = i+1
            break
    position1 = Attack_position[exchange_att-1][0][0]
    position2 = Attack_position[exchange_att-1][0][1]
    storage = copy.deepcopy(Program[position1][0])
    Program[position1][0] = copy.deepcopy(Program[position1][position2])
    Program[position1][position2] = copy.deepcopy(storage)
    unlock_set.append([position1,0+Executed[position1],position2+Executed[position1]])    # 解锁方案集合[第几个DNA，DNA中互换的第一个位置，DNA中互换的第二个位置]
    # 更新攻击位置集合
    # print('换前位置：',Attack_position,'两个位置为：',position1,position2)
    Attack_position = upgradeAttackposition(Program,position1,position2,Attack_position)
    # print('换后位置：',Attack_position)
    for i in range(len(Program)-position1):
        if len(Program[i+position1]) != 0:
            Program[i+position1],Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack = traversexecution(Program[i+position1],Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,i+position1)
    
    return Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,unlock_set

#用换序后的Program信息，更新Attack_position信息
def upgradeAttackposition(Program,position1,position2,Attack_position):
    
    #精准定位，换完就退出循环
    if Program[position1][0][1] == 2:
        for i in range(len(Attack_position[Program[position1][0][0]-1])):
            if Attack_position[Program[position1][0][0]-1][i][0] == position1 and Attack_position[Program[position1][0][0]-1][i][1] == position2:
                Attack_position[Program[position1][0][0]-1][i][1] = 0
                break
    if Program[position1][position2][1] == 2:
        for i in range(len(Attack_position[Program[position1][position2][0]-1])):
            if Attack_position[Program[position1][position2][0]-1][i][0] == position1 and Attack_position[Program[position1][position2][0]-1][i][1] == 0:
                Attack_position[Program[position1][position2][0]-1][i][1] = position2
                break
    return Attack_position

def Logicunlock(chromosome,targets,uavs):
    # print('输入的染色体：', chromosome)
    chromosome = sorted(chromosome, key=(lambda x: x[2]))
    chUAVnum = []
    for i in range(len(chromosome)):
        if chromosome[i][2] not in chUAVnum:
            chUAVnum.append(chromosome[i][2])
    
    # print('交换前染色体：',chromosome)
    Program = []                                         #染色体方案集合
    Detect =[]                                           #已经执行侦查任务的目标集合
    Detect_S = []                                        #侦查任务已经执行，但是攻击任务未被执行完的任务集合
    Attack_num = [0 for _ in range(len(targets))]         #目标攻击次数计数
    Can_evaluate = [0 for _ in range(len(targets))]       #可以执行侦查任务的目标集合
    Evaluation = [0 for _ in range(len(targets))]         #侦查任务执行情况
    Attack_position = [[] for _ in range(len(targets))]   #攻击任务位置集合
    Executed = [0 for _ in range(len(chUAVnum))]         #方案已执行任务集合
    unlock_set = []                                      #解锁策略集合
    target_set = []
    program_attack = [0 for _ in range(len(targets))]

    #第一步提取染色体的方案，统计染色体中的目标，完善Program,Attack_position,target_set
    
    chUAV_qua = [0 for _ in range(len(chUAVnum))]    #记录染色体中每个无人机的执行任务的数量，在染色体解锁过程中需要用到
    
    for i in range(len(chUAVnum)):
        uav_program = []     #每一个uav都有一个执行任务的集合
        order = 0            #用于记录任务次序的,从零开始
        for j in range(len(chromosome)):
            if chUAVnum[i] == chromosome[j][2]:
                chUAV_qua[i] = chUAV_qua[i] + 1      #每个无人机方案的数量统计
                uav_program.append([chromosome[j][0],chromosome[j][1]])
                if chromosome[j][1] == 2:
                    Attack_position[chromosome[j][0]-1].append([i,order])
                    program_attack[chromosome[j][0]-1] = program_attack[chromosome[j][0]-1] + 1
                order = order + 1
                target_set.append(chromosome[j][0])
        Program.append(uav_program)
    target_s = list(set(target_set))      # 方案包含的目标编号
    
    #将染色体中不包含的任务设置成完成
    for i in range(len(Evaluation)):
        if i+1 not in target_s:
            Evaluation[i] = 1
    unlock_pro = []
    while True:
        #大循环和小循环的两个判断参数

        deadlock = 0
        
        # print('循环前的Program',Program)
        # print('循环前的Can_evaluate',Can_evaluate)
        # print('循环前的Attack_position',Attack_position)
        # print('循环前的Executed',Executed)
        # print('循环前的Detect_S',Detect_S)
        # print('循环前的Evaluation',Evaluation)
        #第一块、循环策略1，直至方案维度不发生改变
        jishu = 0
        while deadlock == 0:
            # 先进行一步初始化，运行策略1
            Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,deadlock = unlockStrategy1(Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack)
            jishu = jishu + 1
            # print('策略1循环了',jishu,'次')
        # print('循环后的Program',Program)
        # print('循环后的Can_evaluate',Can_evaluate)
        # print('循环后的Attack_position',Attack_position)
        # print('循环后的Executed',Executed)
        # print('循环后的Detect_S',Detect_S)
        # print('循环后的Evaluation',Evaluation)
        #第二块、进行判断，如果任务集合为空则置参数为0，跳出循环
        lock_jugement = 0
        for i in range(len(Program)):
            lock_jugement = lock_jugement + len(Program[i])
        # print('跳出循环的判断',lock_jugement)
        if lock_jugement == 0:
            break
        
        #第三块、如果锁死，执行以下相应的应对策略
        #如果Derect_S为空集且Detect < 染色体执行目标数，寻找侦查无人机换出（策略2）
        if len(Detect_S) == 0 and len(Detect) < len(target_s):
            # print('执行策略2寻找侦查无人机换出@@@@@@@@@@@@执行策略2寻找侦查无人机换出@@@@@@@@@@@@')
            Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,unlock_set = unlockStrategy2(Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,unlock_set)
        #如果Derect_S为空集且Detect >= 色体执行目标数(应该不可能大于)，寻找攻击无人机换出（策略4）
        elif len(Detect_S) == 0 and len(Detect) == len(target_s):
            # print('执行策略4寻找攻击无人机换出@@@@@@@@@@@@执行策略4寻找攻击无人机换出@@@@@@@@@@@@')
            Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,unlock_set = unlockStrategy4(Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,target_s,unlock_set)
        #如果Derect_S不为空集，寻找能进行攻击无人机换出。（策略3）
        elif len(Detect_S) != 0:
            # print('执行策略3寻找攻击无人机换出@@@@@@@@@@@@执行策略3寻找攻击无人机换出@@@@@@@@@@@@')
            Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,unlock_set = unlockStrategy3(Program,Detect,Detect_S,Attack_num,Can_evaluate,Evaluation,Attack_position,Executed,program_attack,unlock_set)
    unlock_pro = unlock_set
    for i in range(len(unlock_pro)):
        transition_location = 0
        for j in range(unlock_pro[i][0]):
            transition_location = transition_location + chUAV_qua[j]
        location1 = transition_location + unlock_pro[i][1]
        location2 = transition_location + unlock_pro[i][2]
        chromosome_sta = copy.deepcopy(chromosome[location1])
        chromosome[location1] = copy.deepcopy(chromosome[location2])
        chromosome[location2] = copy.deepcopy(chromosome_sta)
    # print('交换后染色体：',chromosome)
    return chromosome

def main(chromosomes,target,UAV):
    new_chromosomes = []
    for chromosome in chromosomes:
        new_chromosome = Logicunlock(chromosome,target,UAV)
        new_chromosomes.append(new_chromosome)
    
    print('解锁后的染色体：',new_chromosomes)

if __name__ == '__main__':
    # target = [1,2,3,4,5,6,7]
    # UAV = [1,2,3,4,5]
    # chromosomes =  [[[3, 3, 1, 11, 32, 1, 1, 1, 1], [2, 2, 2, 12, 14, 12, 1, 1, 2], [1, 2, 2, 13, 14, 12, 1, 1, 2], [3, 2, 2, 12, 14, 12, 1, 1, 2], [5, 2, 2, 6, 14, 12, 1, 1, 2], [6, 2, 2, 26, 14, 12, 1, 1, 2], [7, 1, 3, 28, 3, 14, 1, 1, 3], [5, 3, 3, 10, 3, 14, 1, 1, 3], [2, 2, 3, 12, 3, 14, 1, 1, 3], [2, 3, 3, 16, 3, 14, 1, 1, 3], [3, 2, 3, 28, 3, 14, 1, 1, 3], [6, 1, 3, 2, 3, 14, 1, 1, 3], [6, 3, 3, 14, 3, 14, 1, 1, 3], [3, 1, 4, 21, 9, 23, 1, 1, 4], [5, 1, 4, 9, 9, 23, 1, 1, 4], [1, 1, 4, 28, 9, 23, 1, 1, 4], [1, 3, 4, 29, 9, 23, 1, 1, 4], [7, 3, 4, 7, 9, 23, 1, 1, 4], [2, 1, 5, 31, 3, 2, 1, 1, 5], [7, 2, 5, 28, 3, 2, 1, 1, 5], [4, 2, 5, 30, 3, 2, 1, 1, 5], [4, 1, 5, 25, 0, 0, 0, 1, 5], [4, 3, 5, 10, 0, 0, 0, 1, 5]]]
    
    # target = [1,2,3,4,5,6,7]
    # UAV = [1,2,3,4,5]
    # chromosomes =  [[[4, 3, 1, 3, 31, 29, 1, 1, 1], [5, 3, 1, 29, 31, 29, 1, 1, 1], [2, 3, 1, 32, 31, 29, 1, 1, 1], [2, 1, 1, 18, 31, 29, 1, 1, 1], [4, 2, 2, 11, 15, 34, 1, 1, 2], [6, 2, 2, 16, 15, 34, 1, 1, 2], [7, 2, 2, 3, 15, 34, 1, 1, 2], [2, 2, 2, 17, 15, 34, 1, 1, 2], [2, 2, 3, 25, 5, 30, 1, 1, 3], [3, 1, 3, 4, 5, 30, 1, 1, 3], [4, 1, 3, 35, 5, 30, 1, 1, 3], [6, 1, 3, 29, 5, 30, 1, 1, 3], [5, 2, 3, 35, 5, 30, 1, 1, 3], [1, 1, 4, 16, 27, 32, 1, 1, 4], [5, 1, 4, 30, 27, 32, 1, 1, 4], [7, 1, 4, 35, 27, 32, 1, 1, 4], [7, 3, 5, 9, 30, 14, 1, 1, 5], [1, 2, 5, 13, 30, 14, 1, 1, 5], [1, 3, 5, 15, 30 , 14, 1, 1, 5], [3, 3, 5, 23, 30, 14, 1, 1, 5], [5, 2, 5, 1, 30, 14, 1, 1, 5], [6, 3, 5, 7, 30, 14, 1, 1, 5], [3, 2, 5, 14, 30, 14, 1, 1, 5]]]
    
    # target = [1,2,3,4]
    # UAV = [1,2,3]
    # chromosomes =  [[[2, 1, 1, 1, 9, 13, 1, 1, 1], [2, 3, 1, 29, 9, 13, 1, 1, 1], [3, 1, 1, 3, 9, 13, 1, 1, 1], [4, 1, 1, 22, 9, 13, 1, 1, 1], [4, 3, 1, 4, 9, 13, 1, 1, 1], [1, 2, 2, 15, 23, 27, 2, 1, 2], [2, 2, 2, 12, 23, 27, 2, 1, 2], [3, 2, 2, 35, 23, 27, 2, 1, 2], [1, 1, 3, 10, 1, 26, 2, 2, 1], [1, 3, 3, 16, 1, 26, 2, 2, 1], [3, 3, 3, 13, 1, 26, 2, 2, 1], [4, 2, 3, 26, 1, 26, 2, 2, 1], [3, 2, 3, 20, 27, 14, 2, 2, 1]]]
    
    # target = [1,2,3,4,5,6,7]
    # UAV = [1,2,3,4,5]
    # chromosomes = [[[2, 1, 2, 1, 9, 13, 1, 1, 1], [2, 3,2, 29, 9, 13, 1, 1, 1], [3, 1, 2, 3, 9, 13, 1, 1, 1], [4, 1,2, 22, 9, 13, 1, 1, 1], [4, 3, 2, 4, 9, 13, 1, 1, 1], [1, 2,3, 15, 23, 27, 2, 1, 2], [2, 2, 3, 12, 23, 27, 2, 1, 2], [3, 2, 3, 35, 23, 27, 2, 1, 2], [1, 1, 5, 10, 1, 26, 2, 2, 1], [1, 3, 5, 16, 1, 26, 2, 2, 1], [3, 3, 5, 13, 1, 26, 2, 2, 1], [4, 2, 5, 26, 1, 26, 2, 2, 1], [3, 2, 5, 20, 27, 14, 2, 2, 1]]]
    
    #异常染色体解锁1（同目标被同无人机攻击）(已修改至无问题)
    # target = [1,2,3,4]
    # UAV = [1,2,3]
    # chromosomes =  [[[3, 1, 1, 0, 11, 11, 1, 1, 1], [3, 3, 1, 2, 11, 11, 1, 1, 1], [2, 3, 1, 35, 11, 11, 1, 1, 1], [2, 1, 1, 9, 11, 11, 1, 1, 1], [2, 2, 2, 9, 5, 10, 1, 1, 2], [2, 2, 2, 30, 5, 10, 1, 1, 2], [3, 2, 2, 20, 5, 10, 1, 1, 2]]] 
    
    
    # #解锁异常1（染色体没得毛病）(已修改至无问题)
    # target = [1,2,3,4,5,6,7]
    # UAV = [1,2,3,4,5]
    # chromosomes =  [[[5, 3, 1, 28, 0, 0, 0, 1, 1], [3, 1, 1, 2, 0, 0, 0, 1, 1], [2, 1, 1, 33, 0, 0, 0, 1, 1], [7, 1, 1, 33, 0, 0, 0, 1, 1], [3, 2, 2, 28, 4, 4, 1, 1, 2], [6, 2, 2, 29, 4, 4, 1, 1, 2], [2, 2, 2, 30, 4, 4, 1, 1, 2], [7, 2, 2, 20, 4, 4, 1, 1, 2], [7, 3, 3, 10, 7, 15, 1, 1, 3], [2, 2, 3, 11, 7, 15, 1, 1, 3], [5, 2, 3, 32, 7, 15, 1, 1, 3], [5, 1, 3, 32, 7, 15, 1, 1, 3], [2, 3, 3, 19, 7, 15, 1, 1, 3], [3, 3, 3, 1, 7, 15, 1, 1, 3], [1, 1, 3, 6, 7, 15, 1, 1, 3], [6, 1, 3, 2, 7, 15, 1, 1, 3], [1, 3, 5, 0, 0, 13, 1, 1, 5], [5, 2, 5, 0, 0, 13, 1, 1, 5], [1, 2, 5, 20, 0, 13, 1, 1, 5], [7, 2, 5, 15, 0, 13, 1, 1, 5], [6, 3, 5, 0, 0, 0, 0, 1, 5]]]
    
    #感觉很正常的一个染色体
    target = [1,2,3,4,5,6,7]
    UAV = [1,2,3,4,5]
    chromosomes = [[[7, 1, 1, 28, 23, 4, 1, 1, 1], [1, 1, 1, 16, 23, 4, 1, 1, 1], [7, 3, 1, 14, 23, 4, 1, 1, 1], [5, 2, 2, 24, 12, 35, 1, 1, 2], [7, 2, 2, 35, 12, 35, 1, 1, 2], [1, 2, 2, 15, 12, 35, 1, 1, 2], [2, 2, 2, 20, 12, 35, 1, 1, 2], [3, 2, 2, 29, 12, 35, 1, 1, 2], [5, 2, 3, 5, 9, 18, 1, 1, 3], [5, 3, 3, 30, 15, 21, 1, 1, 3], [6, 1, 3, 1, 15, 21, 1, 1, 3], [6, 2, 3, 1, 13, 6, 1, 1, 3], [1, 3, 4, 27, 0, 0, 0, 1, 4], [2, 1, 4, 11, 0, 0, 0, 1, 4], [6, 3, 4, 2, 0, 0, 0, 1, 4], [2, 3, 4, 26, 0, 0, 0, 1, 4], [5, 1, 5, 34, 24, 33, 1, 1, 5], [3, 1, 5, 33, 24, 33, 1, 1, 5], [2, 2, 5, 35, 24, 33, 1, 1, 5], [6, 2, 5, 31, 24, 33, 1, 1, 5], [3, 3, 5, 31, 0, 0, 0, 1, 5]]]
    main(chromosomes,target,UAV)
