# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2022年06月02日
"""
import chromosome_generation
import math
import new_unlock
import voyage_estimate
import MAP
import return_flight
import time


# 为距离列表和记录列表占位矩阵
def time_placeholder(chromosome, targets):
    tar_attNum = [0 for _ in range(len(targets))]
    for i in range(len(chromosome)):
        if chromosome[i][1] == 2:
            tar_attNum[chromosome[i][0] - 1] = tar_attNum[chromosome[i][0] - 1] + 1
    task_time = []
    record = []
    for i in range(len(tar_attNum)):
        tasklist1 = [0, [], 0, 0]
        tasklist2 = [[0, 0, 0], [], [0, 0, 0], 0]
        if tar_attNum[i] != 0:
            tasklist1[3] = i + 1
            tasklist2[3] = i + 1
            for j in range(tar_attNum[i]):
                tasklist1[1].append(0)
                tasklist2[1].append([0, 0, 0])
            task_time.append(tasklist1)
            record.append(tasklist2)
    return task_time, record


# 任务距离列表更新函数
def task_time_update(chromosome, j, sequence_time, task_time, record, tasksequence):
    # 只需要分为两部分：攻击，（侦查，评估）
    for i in range(len(task_time)):
        # 找出该列DNA所代表的目标在taskdistance的位置
        if task_time[i][-1] == chromosome[j][0]:
            # 情况一：执行攻击任务，即任务类型为2
            if chromosome[j][1] == 2:
                for p in range(len(task_time[i][1])):
                    if task_time[i][1][p] == 0:
                        task_time[i][1][p] = sequence_time
                        record[i][1][p][0] = chromosome[j][2]  # 记录执行该目标该任务的无人机
                        record[i][1][p][1] = tasksequence  # 无人机的第几个任务，从0开始
                        record[i][1][p][2] = j  # 该任务在染色体的第几列
                        break
            # 情况二：执行侦查，评估任务，即任务类型为1,3
            else:
                task_time[i][chromosome[j][1] - 1] = sequence_time  # taskdistance[目标编号定位行][任务类型-1] = 执行时间
                record[i][chromosome[j][1] - 1][0] = chromosome[j][2]  # record[目标编号定位行][任务类型-1][0] = uav编号
                record[i][chromosome[j][1] - 1][1] = tasksequence  # record[目标编号定位行][任务类型-1][1] = uav第几个任务
                record[i][chromosome[j][1] - 1][2] = j  # record[目标编号定位行][任务类型-1][2] = 染色体第几列
    return task_time, record


# 给taskdistance,UAVdistances增加等待圆的函数
# i是任务编号减1，恰好是索引号， j=0 说明要延后攻击任务， j=1说明要延后评估任务，所以j要+1
def waitingroundupgrade(task_time, uav_time_sequences, record, chUAVnum, uavs, i, j, att_tar_add):
    # print('任务距离矩阵：',taskdistance)
    # print('无人机距离矩阵',UAVdistances)
    if len(att_tar_add) == 0:
        # print('记录列表i：', i, '记录列表j：', j+1, '无人机编号：', record[i][j+1][0])
        UAVindex = chUAVnum.index(record[i][j + 1][0])
        # print('无人机编号', UAVindex)
        # 这个无人机之后的所有任务都加等待圆
        for p in range(len(uav_time_sequences[UAVindex]) - record[i][j + 1][1]+1):
            uav_time_sequences[UAVindex][p + record[i][j + 1][1]-1] = uav_time_sequences[UAVindex][
                                                                  p + record[i][j + 1][1]-1] + 2 * math.pi * \
                                                              uavs[record[i][j + 1][0] - 1].turn_radius / uavs[record[i][j + 1][0] - 1].speed
            # 修改完无人机的路径后，更新其在task_time中的值
            for q in range(len(record)):
                for n in range(3):
                    # 如果不是延后攻击任务
                    if n != 1:
                        # 找到延后的无人机，将其后面的所有任务的时间更新
                        if record[q][n][0] == record[i][j + 1][0] and record[q][n][1] == record[i][j + 1][1] + p:
                            task_time[q][n] = uav_time_sequences[UAVindex][p + record[i][j + 1][1]-1]
                    # 延后攻击任务，需要在攻击任务集合中单独找
                    else:
                        for m in range(len(record[q][1])):
                            if record[q][1][m][0] == record[i][j + 1][0] and record[q][1][m][1] == \
                                    record[i][j + 1][1] + p:
                                task_time[q][1][m] = uav_time_sequences[UAVindex][p + record[i][j + 1][1]-1]
    # 对于攻击任务，需要把所有的不符合条件的任务都延后执行
    else:
        for l in att_tar_add:
            # print('不符合的集合：',att_tar_add)
            UAVindex = chUAVnum.index(record[i][1][l][0])
            # print('无人机集合：',chUAVnum,'涉及到的无人机：',record[i][1][l][0],'返回的索引值：',UAVindex)
            # 这个无人机之后的所有任务都加等待圆
            for p in range(len(uav_time_sequences[UAVindex]) - record[i][1][l][1]+1):
                uav_time_sequences[UAVindex][p + record[i][1][l][1]-1] = uav_time_sequences[UAVindex][
                                                                     p + record[i][1][l][1]-1] + 2 * math.pi * \
                                                                 uavs[record[i][1][l][0] - 1].turn_radius/uavs[record[i][1][l][0] - 1].speed
                # 修改完无人机的路径后，更新其在task_time中的值
                for q in range(len(record)):
                    for n in range(3):
                        if n != 1:
                            if record[q][n][0] == record[i][1][l][0] and record[q][n][1] == record[i][1][l][1] + p:
                                task_time[q][n] = uav_time_sequences[UAVindex][p + record[i][1][l][1]-1]
                        else:
                            for m in range(len(record[q][1])):
                                if record[q][1][m][0] == record[i][1][l][0] and record[q][1][m][1] == record[i][1][l][
                                    1] + p:
                                    task_time[q][1][m] = uav_time_sequences[UAVindex][p + record[i][1][l][1]-1]
    return task_time, uav_time_sequences


# 根据两个无人机编号，计算对应目标之间的欧式距离。
def CalculateDistance(point1, point2):
    distance = math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
    return distance


'''
此处下面函数中出现的重要列表进行一些说明；
task_time第二维是每一个目标相应任务被执行时的时间（即无人机执行此任务时已经经历的时间），主要用于满足时序约束。三目标三任务为为例，列表规格：3*3
uav_time_sequences第二维是每一个无人机到各个目标点时航行的路程（时间），这便是适应度函数的值的候选值   
Chromosome是是染色体，也是上述两个距离矩阵的信息连接矩阵，用于通过UAVdistance修改taskdistance
record信息记录矩阵，第二维每一个目标，包含3或4个要执行的任务，第三个维度每一个任务的信息[uav编号，uav第几个任务，染色体第几列]，用于通过taskdistance修改UAVdistance  
此处注意，uav第几个任务是从0开始，即第一个任务编号为0。  三目标三任务为为例，列表规格：3*3*3
chUAVnum 执行任务的无人机编号列表
'''

'''注意此程序中染色体的UVA编号和target编号是否从1开始？如果不是，需要进行修改'''


# 计算两个重要的距离参数矩阵和信息记录矩阵
# 一个染色体中进行的操作，对于整个种群，就需要进行循环计算。
def distanceMatCal(chromosome, targets, uavs, Obstacles):
    # taskdistance存放去执行每一个目标相应任务的距离，tasknums,总任务数，即染色体的长度，用处不大，后期可能删除
    tasknums = len(chromosome)
    return_airport = [[] for i in range(len(uavs))]
    times = []
    # 将对目标的需要执行的任务都提取出来，计算tasknum，为计算taskdistance留出位置。
    task_time, record = time_placeholder(chromosome, targets)

    # 将所有执行任务的无人机编号找出来（分配时，有些无人机未被分配任务）
    chUAVnum = []
    for i in range(len(chromosome)):
        if chromosome[i][2] not in chUAVnum:
            chUAVnum.append(chromosome[i][2])
    # print('执行任务的无人机编号：',chUAVnum)

    uav_time_sequences = []  # 无人机时间序列
    uavtracks = []  # 航迹记录矩阵（复数）
    for i in chUAVnum:
        firstUAV = 1  # 是否是从机场出发执行的第一个任务，是的话为1，否的话为0。
        tasksequence = 0  # UVA第几个任务，初始为0
        uav_time_sequence = []  # 无人机时间序列
        uavtrack = []  # 航迹记录矩阵，[目标点（target编号），行驶距离，染色体中位置]（单数）
        for j in range(len(chromosome)):

            if chromosome[j][2] == i and firstUAV == 1:  # 如果是无人机从机场出发执行的第一个任务，则是从机场飞到当前目标点
                # (1)出发点航程预估距离计算,,,后期使用障碍避免距离函数代替
                point1 = uavs[i - 1].position
                point2 = targets[chromosome[j][0] - 1].position
                # print('机场出发点', point1, point2)
                distance, _ = voyage_estimate.optimal_path_generate(point1, point2, Obstacles)

                # (2)单个UAV的出发执行第一个任务的航迹记录
                flight_time = distance/uavs[i-1].speed
                if len(uav_time_sequence) == 0:
                    uav_time_sequence.append(flight_time)
                else:
                    uav_time_sequence.append(uav_time_sequence[-1] + flight_time)
                tasksequence = tasksequence + 1
                uavtrack.append([chromosome[j][0], flight_time, j])

                # (3)更新任务距离列表和记录列表，即更新task_time,record
                flight_time = uav_time_sequence[-1]
                task_time, record = task_time_update(chromosome, j, flight_time, task_time, record, tasksequence)
                firstUAV = 0

            elif chromosome[j][2] == i and firstUAV == 0:  # 如果无人机不是从机场出发执行的第一个任务，则是从前一目标点飞到当前目标点
                # (1)两目标点Dubins距离计算
                point1 = targets[uavtrack[-1][0] - 1].position
                point2 = targets[chromosome[j][0] - 1].position
                # print('目标到目标', point1, point2)
                distance, _ = voyage_estimate.optimal_path_generate(point1, point2, Obstacles)
                # print('上一目标点是:',uavtrack[-1][0],'上一目标点总航程：',uavtrack[-1][1])
                # print('当前目标点是:',chromosome[j][0],'上一目标点总航程：',distance)

                # (2)单个UAV的两个任务点之间的航迹记录
                flight_time = distance / uavs[i - 1].speed
                if len(uav_time_sequence) == 0:
                    uav_time_sequence.append(flight_time)
                else:
                    uav_time_sequence.append(uav_time_sequence[-1] + flight_time)
                tasksequence = tasksequence + 1
                uavtrack.append([chromosome[j][0], flight_time, j])
                # (3)更新任务距离列表和记录列表，即更新taskdistance,record
                flight_time = uav_time_sequence[-1]
                task_time, record = task_time_update(chromosome, j, flight_time, task_time, record, tasksequence)

        # print('返航',uavtrack)
        # (1)返航距离计算
        star_time = time.time()
        point1 = targets[uavtrack[-1][0] - 1].position
        point2, spend_time = return_flight.return_airport_point(uavs[i-1].airport, uavs[i-1], point1, uav_time_sequence[-1])
        point2 = [round(point2[0]), round(point2[1])]
        return_airport[i-1] = [uavs[i-1].airport.num, point2, spend_time, i]
        end_time = time.time()
        times.append(end_time - star_time)
        # print('返航路径点', point1, point2)
        distance, _ = voyage_estimate.optimal_path_generate(point1, point2, Obstacles)

        # (2)单个UAV的归程航迹记录
        flight_time = distance / uavs[i - 1].speed
        if len(uav_time_sequence) == 0:
            uav_time_sequence.append(flight_time)
        else:
            uav_time_sequence.append(uav_time_sequence[-1] + flight_time)
        uavtrack.append([-1, flight_time, -1])  # 第一个编号-1表示机场，第二个编号-1表示不再染色体中（返回机场）

        # (3)总体航迹记录
        uav_time_sequences.append(uav_time_sequence)
        uavtracks.append(uavtrack)

    '''
    上述程序完成对于4个主要列表的计算
    task_time    用于判断是否上锁
    record          用于通过taskdistance修改UAVdistance
    uavtracks       用于记录航迹，便于计算dubins路径
    uav_time_sequence  用于记录uav的时间，但目标函数是时间时使用该指标
    '''
    return_flight_time = sum(times)
    return task_time, uav_time_sequences, record, tasknums, chUAVnum, return_flight_time, return_airport


# 判断染色体是否满足时序约束，满足输出lock=0，不满足则输出lock=1
def timingConst(task_time, uav_time_sequences, record, tasknums, chUAVnum, uavs):
    # 时序约束
    # waitinground = 60
    jugement = 1  # 判断条件，不满足时序约束时为1，默认为1
    jishu = 0  # 一个计数，当其达到一定程度就判断锁死
    lock = 0  # 染色体是否锁死，做为函数返回值
    while jugement == 1:
        jishu = jishu + 1
        jugement = 0
        for i in range(len(task_time)):
            for j in range(2):
                # 判断攻击任务是否先于侦查任务，增加攻击任务等待圆(需要更改多个无人机)
                att_tar_add = []
                # j = 0判断攻击任务有没有先于侦查任务的
                if j == 0:
                    # 将先于侦查任务的攻击任务提取出来
                    for k in range(len(task_time[i][1])):
                        if task_time[i][1][k] <= task_time[i][j]:
                            att_tar_add.append(k)
                            jugement = 1
                    # 如果是空集，则说明没有问题，不做处理
                    if len(att_tar_add) != 0:
                        task_time, uav_time_sequences = waitingroundupgrade(task_time, uav_time_sequences, record, chUAVnum,
                                                                         uavs, i, j, att_tar_add)
                # 判断评估任务是否先于攻击任务，增加评估任务等待圆(只需更改一个无人机)
                else:
                    if task_time[i][j + 1] <= max(task_time[i][1]):
                        jugement = 1
                        task_time, uav_time_sequences = waitingroundupgrade(task_time, uav_time_sequences, record, chUAVnum,
                                                                         uavs, i, j, att_tar_add)

        if jishu > 80 * tasknums:
            lock = 1
            break
    return lock


def waiting_circle_statistics(task_time, uav_time_sequences, record, chUAVnum, uavs):
    # 时序约束
    jugement = 1  # 判断条件，不满足时序约束时为1，默认为1
    waiting_list = [[0, 0] for i in range(len(task_time))]
    while jugement == 1:
        # jugement = 0
        for i in range(len(task_time)):
            for j in range(2):
                # 判断攻击任务是否先于侦查任务，增加攻击任务等待圆(需要更改多个无人机)
                att_tar_add = []
                # j = 0判断攻击任务有没有先于侦查任务的
                if j == 0:
                    # 将先于侦查任务的攻击任务提取出来
                    for k in range(len(task_time[i][1])):
                        if task_time[i][1][k] <= task_time[i][j]:
                            att_tar_add.append(k)
                            jugement = 1
                    # 如果是空集，则说明没有问题，不做处理
                    if len(att_tar_add) != 0:
                        task_time, uav_time_sequences = waitingroundupgrade(task_time, uav_time_sequences, record, chUAVnum,
                                                                         uavs, i, j, att_tar_add)
                        waiting_list[i][j] = waiting_list[i][j]+1
                # 判断评估任务是否先于攻击任务，增加评估任务等待圆(只需更改一个无人机)
                else:
                    if task_time[i][j + 1] <= max(task_time[i][1]):
                        jugement = 1
                        task_time, uav_time_sequences = waitingroundupgrade(task_time, uav_time_sequences, record, chUAVnum,
                                                                         uavs, i, j, att_tar_add)
                        waiting_list[i][j] = waiting_list[i][j] + 1

    return waiting_list, task_time, uav_time_sequences


# 适应度计算，主程序
def fitness(chromosomes, targets, uavs, Obstacles):
    fitness = []
    time_set = []
    return_airports = []
    for i in range(len(chromosomes)):
        maxdistance = 0
        while True:
            chromosomes[i] = new_unlock.Logicunlock(chromosomes[i], targets, uavs)
            task_time, uav_time_sequences, record, tasknums, chUAVnum, return_flight_time, return_airport = distanceMatCal(chromosomes[i], targets, uavs, Obstacles)
            lock = timingConst(task_time, uav_time_sequences, record, tasknums, chUAVnum, uavs)
            if lock == 1:
                chromosomes[i] = new_unlock.Logicunlock(chromosomes[i], targets, uavs)
                print('进行过解锁')
            else:
                break
        for uavdis in uav_time_sequences:
            if uavdis[-1] > maxdistance:
                maxdistance = uavdis[-1]
        time_set.append(return_flight_time)
        fitness.append(maxdistance)
        return_airports.append(return_airport)
    time_sum = sum(time_set)
    return fitness, time_sum, return_airports


def main(targets, uavs, Obstacles, population):
    chromosomes, resources = chromosome_generation.codingChromosome(targets, uavs, population)
    pop_fitness = fitness(chromosomes, targets, uavs, Obstacles)
    print('最优值是：', pop_fitness)
    print('染色体为：', chromosomes)


if __name__ == '__main__':
    Uav = [[[4300, 1800], 1, 80, 0, 250], [[4300, 1800], 3, 60, 5, 220], [[4300, 1800], 2, 70, 3, 200]]
    obstacles = [[1, [[1000, 1500], 200]], [1, [[1500, 3500], 500]], [1, [[4500, 2500], 100]],
                 [1, [[3000, 1500], 200]], [1, [[3500, 4500], 50]],
                 [2, [[3000, 2500], [3500, 2700], [3800, 3100], [3300, 3500], [2600, 3000]]],
                 [2, [[1800, 2100], [2300, 2200], [2400, 2500], [1900, 2600]]]]
    target = [[[2500, 3600], [1, 2, 3], 40], [[500, 2000], [1, 2, 3], 60], [[4750, 3000], [1, 2, 3], 40],
              [[250, 4500], [1, 2, 3], 80], [[2000, 1500], [1, 2, 3], 80]]
    targets = []
    uavs = []
    Obstacles = []
    for i in range(len(target)):
        c_tar = chromosome_generation.Target(i + 1, target[i][0], target[i][1], target[i][2])
        targets.append(c_tar)
    for i in range(len(Uav)):
        c_uav = chromosome_generation.UAV(i + 1, Uav[i][0], Uav[i][1], Uav[i][2], Uav[i][3], Uav[i][4])
        uavs.append(c_uav)
    for obstacle in obstacles:
        if obstacle[0] == 1:
            Obs = MAP.Obstacle('o', obstacle[1])
        else:
            Obs = MAP.Obstacle('p', obstacle[1])
        Obstacles.append(Obs)
    main(targets, uavs, Obstacles, 100)
