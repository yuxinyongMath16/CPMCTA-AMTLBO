# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2022年10月05日
"""
import numpy as np
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt
import digital_aircraft
import voyage_estimate
import math
import random
import unlock
import return_flight


def calculation_waiting_circle(chromosome, targets, uavs, Obstacles):
    task_time, uav_time_sequences, record, tasknums, chUAVnum, return_flight_time, return_airport = \
        unlock.distanceMatCal(chromosome, targets, uavs, Obstacles)
    print('任务时间序列', task_time)
    print('无人机时间序列', uav_time_sequences)
    print('信息记录矩阵', record)
    waiting_list, task_time, uav_time_sequences = unlock.waiting_circle_statistics(task_time, uav_time_sequences, record, chUAVnum, uavs)
    print('增加等待圆后的任务时间序列', task_time)
    print('增加等待圆后的无人机时间序列', uav_time_sequences)
    uav_waiting_information = find_waiting_circle(waiting_list, chromosome, targets)
    return uav_waiting_information


def find_uav_num(i, j, chromosome):
    current_uav_num = chromosome[0][2]
    for p in range(len(chromosome)):
        if chromosome[p][2] != current_uav_num:
            current_uav_num = chromosome[p][2]
        if chromosome[p][0] == i+1 and chromosome[p][1] == j+2:
            uav_num = current_uav_num
            return uav_num


def find_waiting_circle(waiting_list, chromosome, targets):
    uav_waiting_information = []
    for i in range(len(waiting_list)):
        for j in range(2):
            if waiting_list[i][j] != 0:
                uav_num = find_uav_num(i, j, chromosome)
                uav_target_position = targets[i].position
                uav_waiting_information.append([uav_num, uav_target_position, waiting_list[i][j]])
    return uav_waiting_information


def add_waiting_circle(Wpts, wpt, uav_waiting_information):
    for i in range(len(uav_waiting_information)):
        for j in range(len(wpt)):
            # print('等待圆中的编号', uav_waiting_information[i][0], '无人机编号', wpt[j], '序列编号', j)
            if uav_waiting_information[i][0] == wpt[j]:
                for p in range(len(Wpts[j])):
                    if Wpts[j][p][0] == uav_waiting_information[i][1]:
                        # print('此处应该插入一个值, 插入前的序列', Wpts[j])
                        Wpts[j].insert(p+1, [Wpts[j][p][0], uav_waiting_information[i][2]])
                        # print('插后的序列', Wpts[j])
                        break
    return Wpts


def draw_circle(core, r):
    theta = np.arange(0, 2 * np.pi, 0.01)
    x = core[0] + r * np.cos(theta)
    y = core[1] + r * np.sin(theta)
    plt.plot(x, y, 'k')


def draw_polygons(points):
    x = []
    y = []
    for point in points:
        x.append(point[0])
        y.append(point[1])
    x.append(x[0])
    y.append(y[0])
    plt.plot(x, y, 'k-')


def path_transform(path):
    path_x = []
    path_y = []
    for pa in path:
        path_x.append(pa[0])
        path_y.append(pa[1])
    return [path_x, path_y]


def calculate_direction(last_node, now_node):
    # print('执行角度更新,初始点是：', last_node, '最终点是：', now_node)
    if now_node[0] - last_node[0] == 0:
        # print('无斜率')
        if now_node[1] - last_node[1] >= 0:
            direction = math.pi / 2
        else:
            direction = math.pi * 3 / 2
    else:
        k = (now_node[1] - last_node[1]) / (now_node[0] - last_node[0])
        # print('斜率是：', k)
        if now_node[0] - last_node[0] < 0:
            direction = math.pi + math.atan(k)
        else:
            if math.atan(k) > 0:
                direction = math.atan(k)
                # print('反正切函数是：', math.atan(k))
            else:
                direction = math.pi * 2 + math.atan(k)
    return direction


def calculate_distance(point1, point2):
    distance = math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
    return distance


# 没有等待圆
def uav_time_set_calculate(Wpts, wpt, uavs):
    uav_time_set = [[] for i in range(len(Wpts))]
    for i in range(len(Wpts)):
        for j in range(len(Wpts[i])-1):
            if len(uav_time_set[i]) == 0:
                if Wpts[i][j+1][1] == 0:
                    uav_time = calculate_distance(Wpts[i][j][0], Wpts[i][j+1][0])/uavs[wpt[i]-1].speed
                else:
                    uav_time = 2*math.pi*uavs[wpt[i]-1].turn_radius*Wpts[i][j+1][1]/uavs[wpt[i]-1].speed
            else:
                if Wpts[i][j+1][1] == 0:
                    uav_time = calculate_distance(Wpts[i][j][0], Wpts[i][j+1][0])/uavs[wpt[i]-1].speed + uav_time_set[i][-1]
                else:
                    uav_time = 2*math.pi*uavs[wpt[i]-1].turn_radius*Wpts[i][j+1][1]/uavs[wpt[i]-1].speed + uav_time_set[i][-1]
            uav_time_set[i].append(uav_time)
    return uav_time_set


# uav当前点计算程序
def uav_time_sequence(Wpts, uav_time_set, i, j, time, uav_speed):
    way_point = []
    for p in range(j+1):
        # if Wpts[i][p][0] not in way_point:
        way_point.append(Wpts[i][p][0])
    # print('查看序列是否是等待圆', Wpts[i][j+1])
    if Wpts[i][j+1][1] == 0:
        uav_direction = calculate_direction(Wpts[i][j][0], Wpts[i][j+1][0])
        if j != 0:
            past_time = uav_time_set[i][j-1]
        else:
            past_time = 0
        time_slice = time - past_time
        current_location = [Wpts[i][j][0][0]+time_slice*uav_speed*math.cos(uav_direction),
                            Wpts[i][j][0][1]+time_slice*uav_speed*math.sin(uav_direction)]
        way_point.append(current_location)
    # else:
    #     uav_direction1 = calculate_direction(Wpts[i][j][0], Wpts[i][j + 1][0])
    #     past_time = uav_time_set[i][j - 1]
    #     time_slice = time - past_time

    return way_point


def add_return_airport_position(Wpts, wpt, uavs, Obstacles):
    uav_time_set = uav_time_set_calculate(Wpts, wpt, uavs)
    for i in range(len(Wpts)):
        air_point, _ = return_flight.return_airport_point(uavs[wpt[i] - 1].airport, uavs[wpt[i] - 1],
                                                                   Wpts[i][-1][0], uav_time_set[i][-1])
        _, points_path = voyage_estimate.optimal_path_generate(Wpts[i][-1][0], air_point, Obstacles)
        if len(points_path) > 0:
            for point in points_path[0]:
                if point != Wpts[i][-1][0]:
                    Wpts[i].append([point, 0])
    return Wpts


def calculate_program_time(Wpts, wpt, uavs):
    uav_time_set = uav_time_set_calculate(Wpts, wpt, uavs)
    program_time = 0
    for time_set in uav_time_set:
        if time_set[-1] > program_time:
            program_time = time_set[-1]
    return program_time


def generate_uav_frame(Wpts, time, wpt, uavs):
    uavs_way_point = []
    uav_time_set = uav_time_set_calculate(Wpts, wpt, uavs)
    # print('时间集合', uav_time_set)
    # print('时间集合长度是', len(uav_time_set))
    for i in range(len(uav_time_set)):
        for j in range(len(uav_time_set[i])):
            if j != 0:
                # 第一段路程已经走完
                if uav_time_set[i][j-1] < time <= uav_time_set[i][j]:
                    uav_way_point = uav_time_sequence(Wpts, uav_time_set, i, j, time, uavs[wpt[i]-1].speed)
                    uavs_way_point.append(uav_way_point)
                elif time > uav_time_set[i][-1]:
                    uav_way_point = []
                    for p in range(len(Wpts[i])):
                        uav_way_point.append(Wpts[i][p][0])
                    uavs_way_point.append(uav_way_point)
                    break
            else:
                # 第一段路程还没有走完
                if time <= uav_time_set[i][0]:
                    uav_way_point = uav_time_sequence(Wpts, uav_time_set, i, j, time, uavs[wpt[i]-1].speed)
                    uavs_way_point.append(uav_way_point)
    return uavs_way_point


def generate_airport_frame(airport_track, time, airports):
    airport_way_point = []
    for i in range(len(airport_track)):
        way_point = [airport_track[i][0]]
        next_point = [airport_track[i][0][0]+airports[i].speed*time*math.cos(airports[i].direction),
                      airport_track[i][0][1]+airports[i].speed*time*math.sin(airports[i].direction)]
        way_point.append(next_point)
        airport_way_point.append(way_point)
    return airport_way_point


def track_map(optimal_chromosome, uavs, targets, airports, Obstacles, return_airport, optimal_value):
    # 绘图
    wpt = []   # 方案中拥有的无人机编号
    position = []
    for i in range(len(optimal_chromosome)):
        if optimal_chromosome[i][2] not in wpt:
            wpt.append(optimal_chromosome[i][2])  # 存放执行任务的无人机编号
            position.append(i)  # 不同编号的无人机在染色体第一次出现的位置
    Wpts = []

    for i in range(len(wpt)):
        Wpt = []
        point1 = uavs[wpt[i]-1].position
        # print('第',i,'次机场出发',point1.x,point1.y,point1.psi)
        Wpt.append([point1, 0])
        # print('第几个无人机', i+1)
        for j in range(len(optimal_chromosome)):
            if optimal_chromosome[j][2] == wpt[i]:
                if Wpt:  # 列表不为空执行，可能出现一个UAV只执行一个任务的情况
                    # print('路径点集合', Wpt, '路径点集合的最后一位', Wpt[-1], '目标坐标', targets[optimal_chromosome[j][0] - 1].position)
                    _, points_path = voyage_estimate.optimal_path_generate(Wpt[-1][0],
                                                                           targets[optimal_chromosome[j][0] - 1].position,
                                                                           Obstacles)
                    if len(points_path) > 0:
                        for point in points_path[0]:
                            if point != Wpt[-1][0]:
                                Wpt.append([point, 0])
        # point3 = uavs[wpt[i]-1].position
        # point3 = return_airport[wpt[i]-1][1]
        # _, points_path = voyage_estimate.optimal_path_generate(Wpt[-1][0], point3, Obstacles)
        # if len(points_path) > 0:
        #     for point in points_path[0]:
        #         if point != Wpt[-1][0]:
        #             Wpt.append([point, 0])
        Wpts.append(Wpt)
    # 轨迹中增加等待圆
    uav_waiting_information = calculation_waiting_circle(optimal_chromosome, targets, uavs, Obstacles)
    Wpts = add_waiting_circle(Wpts, wpt, uav_waiting_information)
    # 轨迹中增加返回的机场位置
    Wpts = add_return_airport_position(Wpts, wpt, uavs, Obstacles)
    print('等待圆信息', uav_waiting_information, '路径信息', Wpts)
    #

    pic_color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'b', 'g', 'r']
    move_airport = [[[air.init_position, 0, 0]] for air in airports]
    for i in range(len(move_airport)):
        for j in range(len(return_airport)):
            # print('返回机场信息', return_airport)
            if len(return_airport[j]) != 0:
                if return_airport[j][0] - 1 == i:
                    # [位置]，时间，无人机编号
                    move_airport[i].append([return_airport[j][1], return_airport[j][2], return_airport[j][3]])
                    move_airport[i] = sorted(move_airport[i], key=(lambda x: x[1]))
    pic_label = []
    for i in range(len(uavs)):
        label1 = 'UAV' + ' ' + str(i + 1)
        pic_label.append(label1)
    # print(pic_label)

    tar_label = []
    for i in range(len(targets)):
        label2 = 'Target' + ' ' + str(i + 1)
        tar_label.append(label2)
    # print(tar_label)

    air_label = []
    for i in range(len(airports)):
        label3 = 'Airport' + ' ' + str(i + 1)
        air_label.append(label3)
    # print(tar_label)

    airport_track = []
    for i in range(len(move_airport)):
        track = []
        for j in range(len(move_airport[i])):
            if j == 0:
                track.append(move_airport[i][j][0])
            else:
                track.append(move_airport[i][j][0])
        airport_track.append(track)

    time = 0
    step_length = 2
    program_time = calculate_program_time(Wpts, wpt, uavs)
    # 画图部分锁死
    while time < program_time:
        print('当前时间', time)
        # 绘制目标及障碍
        plt.figure()
        for obs in Obstacles:
            if obs.type == 'o':
                draw_circle(obs.information[0], obs.information[1])
            else:
                draw_polygons(obs.information)
        for target in targets:
            random.seed(1)
            target_direction = random.random() * 2 * math.pi
            vehicle_position = digital_aircraft.digital_target_ship(target.position, 500, target_direction)
            plt.fill(vehicle_position[0], vehicle_position[1], color='cornflowerblue')
            plt.plot(vehicle_position[0], vehicle_position[1], 'k', linewidth=0.5)
        # 绘制初始机场
        # for i in range(len(move_airport)):
        #     track_direction = calculate_direction(move_airport[i][0][0], move_airport[i][1][0])
        #     vehicle_position = digital_aircraft.digital_aircraft_carrier(move_airport[i][0][0], 500,
        #                                                                  track_direction)
        #     plt.fill(vehicle_position[0], vehicle_position[1], color='k')
        #     plt.plot(vehicle_position[0], vehicle_position[1], 'k', linewidth=0.5)
        # 绘制机场的移动轨迹
        airport_way_point = generate_airport_frame(airport_track, time, airports)
        for p in range(len(airport_way_point)):
            total_path = path_transform(airport_way_point[p])
            plt.plot(total_path[0], total_path[1], pic_color[p] + ':', label=air_label[p])
            track_direction = airports[p].direction
            # 机场（陆基）  digital_airport
            # 航母（海基） digital_aircraft_carrier
            # 运输机（空基）  digital_transporter
            if airports[p].air_type == 1:
                vehicle_position = digital_aircraft.digital_airport(airport_way_point[p][-1], 500, track_direction)
            elif airports[p].air_type == 2:
                vehicle_position = digital_aircraft.digital_aircraft_carrier(airport_way_point[p][-1], 500, track_direction)
            elif airports[p].air_type == 3:
                vehicle_position = digital_aircraft.digital_transporter(airport_way_point[p][-1], 700, track_direction - math.pi/2)
            plt.fill(vehicle_position[0], vehicle_position[1], color=pic_color[move_airport[i][j][2] - 1])
            plt.plot(vehicle_position[0], vehicle_position[1], 'b', linewidth=0.5)
        # 绘制time时刻UAV的航迹图
        uavs_way_point = generate_uav_frame(Wpts, time, wpt, uavs)
        for p in range(len(uavs_way_point)):
            # print('无人机运动序列', uavs_way_point[p][-1])
            if uavs_way_point[p][-1] != Wpts[p][-1][0]:
                # print('p值', p, uavs_way_point[p])
                track_direction = calculate_direction(uavs_way_point[p][-2], uavs_way_point[p][-1])
                if uavs[wpt[p]-1].type == 1:
                    vehicle_position = digital_aircraft.digital_reconnaissance_uav(uavs_way_point[p][-1], 500,
                                                                                   track_direction - math.pi / 2)
                elif uavs[wpt[p]-1].type == 2:
                    vehicle_position = digital_aircraft.digital_combat_uav(uavs_way_point[p][-1], 500,
                                                                           track_direction - math.pi / 2)
                elif uavs[wpt[p]-1].type == 3:
                    vehicle_position = digital_aircraft.digital_ammunition_uav(uavs_way_point[p][-1], 500,
                                                                               track_direction - math.pi / 2)
                plt.fill(vehicle_position[0], vehicle_position[1], color=pic_color[p])
                plt.plot(vehicle_position[0], vehicle_position[1], 'k', linewidth=0.5)
            # print('绘图次数：', p + 1, '总绘图次数', len(uavs_way_point), '路径为', uavs_way_point[p])
            total_path = path_transform(uavs_way_point[p])
            UAV_NUM_label = wpt[p]
            # print('绘图列表', total_path)
            plt.plot(total_path[0], total_path[1], pic_color[p], label=pic_label[UAV_NUM_label - 1], linewidth=0.8)
            plt.legend(loc=0, ncol=1)
        plt.xlabel('X(m)')
        plt.ylabel('Y(m)')
        plt.axis('equal')  # 设置x，y轴等刻度
        plt.rcParams['savefig.dpi'] = 300  # 图片像素
        plt.rcParams['figure.dpi'] = 300  # 分辨率
        filename = "track_" + str(int(time/step_length+1)).zfill(4) + ".png"
        plt.savefig(filename)
        time = time + step_length