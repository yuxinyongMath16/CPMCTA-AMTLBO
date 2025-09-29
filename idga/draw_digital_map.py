# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2022年10月05日
"""
import numpy as np
import matplotlib.pyplot as plt
import digital_aircraft
import voyage_estimate
import math
import random


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


def track_map(optimal_chromosome, uavs, targets, airports, Obstacles, return_airport):
    # 绘图
    wpt = []
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
        Wpt.append(point1)
        # print('第几个无人机', i+1)
        for j in range(len(optimal_chromosome)):
            if optimal_chromosome[j][2] == wpt[i]:
                if Wpt:  # 列表不为空执行，可能出现一个UAV只执行一个任务的情况
                    # print('路径点集合', Wpt, '路径点集合的最后一位', Wpt[-1], '目标坐标', targets[optimal_chromosome[j][0] - 1].position)
                    _, points_path = voyage_estimate.optimal_path_generate(Wpt[-1],
                                                                           targets[optimal_chromosome[j][0] - 1].position,
                                                                           Obstacles)
                    if len(points_path) > 0:
                        for point in points_path[0]:
                            if point != Wpt[-1]:
                                Wpt.append(point)
        # point3 = uavs[wpt[i]-1].position
        point3 = return_airport[wpt[i]-1][1]
        _, points_path = voyage_estimate.optimal_path_generate(Wpt[-1], point3, Obstacles)
        if len(points_path) > 0:
            for point in points_path[0]:
                if point != Wpt[-1]:
                    Wpt.append(point)
        Wpts.append(Wpt)

    pic_color = ['b', 'g', 'r', 'c', 'm', 'y', 'k', 'b', 'g', 'r']
    marker = ['v', 's', 'd', 'p', 'h', 'o']
    move_airport = [[[air.init_position, 0, 0]] for air in airports]
    for i in range(len(move_airport)):
        for j in range(len(return_airport)):
            print('返回机场信息', return_airport)
            if len(return_airport[j]) != 0:
                if return_airport[j][0] - 1 == i:
                    move_airport[i].append([return_airport[j][1], return_airport[j][2], return_airport[j][3]])
                    move_airport[i] = sorted(move_airport[i], key=(lambda x: x[1]))
    print('机场信息', move_airport)
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

    # 绘制目标及障碍
    plt.figure()
    for obs in Obstacles:
        if obs.type == 'o':
            draw_circle(obs.information[0], obs.information[1])
        else:
            draw_polygons(obs.information)
    for target in targets:
        target_direction = random.random()*2*math.pi
        vehicle_position = digital_aircraft.digital_target_ship(target.position, 500, target_direction)
        plt.fill(vehicle_position[0], vehicle_position[1], color='cornflowerblue')
        plt.plot(vehicle_position[0], vehicle_position[1], 'k', linewidth=0.5)
    airport_track = []
    for i in range(len(move_airport)):
        track = []
        for j in range(len(move_airport[i])):
            if j == 0:
                track.append(move_airport[i][j][0])
                track_direction = calculate_direction(move_airport[i][j][0], move_airport[i][j+1][0])
                vehicle_position = digital_aircraft.digital_aircraft_carrier(move_airport[i][j][0], 500, track_direction)
                plt.fill(vehicle_position[0], vehicle_position[1], color='k')
                plt.plot(vehicle_position[0], vehicle_position[1], 'k', linewidth=0.5)
            else:
                track.append(move_airport[i][j][0])
                track_direction = calculate_direction(move_airport[i][j-1][0], move_airport[i][j][0])
                vehicle_position = digital_aircraft.digital_aircraft_carrier(move_airport[i][j][0], 500, track_direction)
                plt.fill(vehicle_position[0], vehicle_position[1], color=pic_color[move_airport[i][j][2]-1])
                plt.plot(vehicle_position[0], vehicle_position[1], 'k', linewidth=0.5)
        airport_track.append(track)

    # 绘制机场的移动轨迹
    for p in range(len(airport_track)):
        total_path = path_transform(airport_track[p])
        plt.plot(total_path[0], total_path[1], pic_color[p]+':', label=air_label[p])

    # 绘制无人机飞行路线图
    for p in range(len(Wpts)):
        for q in range(len(Wpts[p])-1):
            track_direction = calculate_direction(Wpts[p][q], Wpts[p][q+1])
            centre_position = [(Wpts[p][q][0] + Wpts[p][q+1][0])/2, (Wpts[p][q][1] + Wpts[p][q+1][1])/2]
            if uavs[p].type == 1:
                vehicle_position = digital_aircraft.digital_reconnaissance_uav(centre_position, 500, track_direction-math.pi/2)
            elif uavs[p].type == 2:
                vehicle_position = digital_aircraft.digital_combat_uav(centre_position, 500, track_direction-math.pi/2)
            elif uavs[p].type == 3:
                vehicle_position = digital_aircraft.digital_ammunition_uav(centre_position, 500, track_direction-math.pi/2)
            plt.fill(vehicle_position[0], vehicle_position[1], color=pic_color[p])
            plt.plot(vehicle_position[0], vehicle_position[1], 'k', linewidth=0.5)
        print('绘图次数：', p+1, '总绘图次数', len(Wpts), '路径为', Wpts[p])
        total_path = path_transform(Wpts[p])
        UAV_NUM_label = wpt[p]
        print('绘图列表', total_path)
        plt.plot(total_path[0], total_path[1], pic_color[p], label=pic_label[UAV_NUM_label - 1], linewidth=0.8)
        plt.legend(loc=0, ncol=1)
    plt.xlabel('X(m)')
    plt.ylabel('Y(m)')
    plt.axis('equal')  # 设置x，y轴等刻度
    plt.rcParams['savefig.dpi'] = 300  # 图片像素
    plt.rcParams['figure.dpi'] = 300  # 分辨率
    plt.show()