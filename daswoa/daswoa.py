# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2022年11月09日
daswoa主程序
"""


import voyage_estimate
import time
import math
import MAP
import numpy as np
import population_generation
import population_generation_fix
import population_generation_fix1
import fitness_calculation
import population_update
import local_search
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


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
        plt.plot(target.position[0], target.position[1], 'r*', markersize=7)
    airport_track = []
    for i in range(len(move_airport)):
        track = []
        for j in range(len(move_airport[i])):
            if j == 0:
                track.append(move_airport[i][j][0])
                plt.plot(move_airport[i][j][0][0], move_airport[i][j][0][1], 'k'+marker[i], markersize=7)
            else:
                track.append(move_airport[i][j][0])
                plt.plot(move_airport[i][j][0][0], move_airport[i][j][0][1], pic_color[move_airport[i][j][2]-1]+marker[i], markersize=7)
        airport_track.append(track)

    for p in range(len(airport_track)):
        total_path = path_transform(airport_track[p])
        plt.plot(total_path[0], total_path[1], pic_color[p]+':', label=air_label[p])

    pic_num = 7
    # 绘制无人机飞行路线图
    for p in range(len(Wpts)):
        # if p == pic_num:
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
    filename = "task_assignment" + ".png"
    plt.savefig(filename)


def main(max_iter, population_size, uavs, targets, Obstacles, threat_r):
    start = time.time()
    move_air_time = []
    iteration_optimal_value = []
    iteration_f1_value = []
    iteration_f2_value = []
    # 程序初始化
    # solutions, resources = population_generation_fix1.fixed_population_new1_1()
    solutions, resources = population_generation_fix.fixed_population_new11_1()
    # print('产生解的初始值', solutions)
    # print('产生资源的初始值', resources)
    iter_num = 0
    while True:

        pop_fitness, time_sum, return_airports, pop_f1, pop_f2 = fitness_calculation.fitness(solutions, targets, uavs, Obstacles, threat_r)
        iter_num = iter_num + 1
        if iter_num > max_iter:
            break
        print('迭代次数：', iter_num)
        print('此代最优值是', min(pop_fitness))
        move_air_time.append(time_sum)
        if iter_num % 10 == 0 or iter_num == 1:
            optimal_value1 = min(pop_fitness)
            optimal_index = pop_fitness.index(min(pop_fitness))
            optimal_f1 = pop_f1[optimal_index]
            optimal_f2 = pop_f2[optimal_index]
            iteration_optimal_value.append(optimal_value1)
            iteration_f1_value.append(optimal_f1)
            iteration_f2_value.append(optimal_f2)

        solutions, resources = population_update.population_update(iter_num, max_iter, solutions, resources, uavs, targets, Obstacles, threat_r)
        solutions, resources = local_search.local_search(solutions, resources, 1)

    optimal_value = min(pop_fitness)
    optimal_index = pop_fitness.index(min(pop_fitness))
    print('最优值是：', optimal_value)
    optimal_solution = solutions[optimal_index]
    optimal_solution_airport = return_airports[optimal_index]
    print('最优方案为：', optimal_solution)
    print('最优方案的机场', optimal_solution_airport)
    end = time.time()
    run_time = end - start
    print("Runtime is ：", run_time)  # 计时结果！！！
    # print('程序计算移动机场总耗时是', sum(move_air_time))
    return optimal_solution, iteration_optimal_value, run_time, iteration_f1_value, iteration_f2_value


if __name__ == '__main__':
    # 3556算例数据
    airport = [[[10000, 60000], 0, 0], [[20000, 17000], 16, math.pi / 4], [[-16000, 10000], 50, math.pi / 2]]
    Uav = [[[10000, 60000], 1, 80, 0, 250], [[10000, 60000], 2, 70, 3, 200, 3], [[20000, 17000], 3, 80, 4, 220],
           [[20000, 17000], 2, 70, 2, 200], [[-16000, 10000], 1, 80, 0, 250, 3]]
    obstacles = [[1, [[10000, 15000], 2000]], [1, [[15000, 35000], 5000]], [1, [[0, 53000], 3000]],
                 [2, [[30000, 42000], [35000, 44000], [38000, 48000], [33000, 52000], [26000, 47000]]],
                 [2, [[-8000, 11000], [-3000, 12000], [-2000, 15000], [-7000, 16000]]],
                 [2, [[-2000, 28000], [1500, 30000], [1000, 33000], [-4000, 34000], [-8000, 31500], [-6500, 29000]]]]
    target = [[[5000, 20000], [1, 2, 3], 60, 2], [[15000, 23000], [1, 2, 3], 70, 2], [[25000, 36000], [1, 2, 3], 40, 2],
              [[16000, 49000], [1, 2, 3], 60, 2], [[-2000, 41000], [1, 2, 3], 80, 2]]
    # 3676算例数据
    # airport = [[[10000, 60000], 0, 0], [[20000, 17000], 16, math.pi / 4], [[-16000, 10000], 50, math.pi / 2]]
    # Uav = [[[10000, 60000], 1, 80, 0, 250], [[10000, 60000], 2, 70, 3, 200, 3], [[20000, 17000], 3, 80, 4, 220],
    #        [[20000, 17000], 2, 70, 2, 200], [[-16000, 10000], 1, 80, 0, 250, 3], [[-16000, 10000], 3, 60, 5, 220]]
    #
    # obstacles = [[1, [[10000, 15000], 2000]], [1, [[15000, 35000], 5000]], [1, [[0, 53000], 3000]],
    #              [2, [[30000, 42000], [35000, 44000], [38000, 48000], [33000, 52000], [26000, 47000]]],
    #              [2, [[-8000, 11000], [-3000, 12000], [-2000, 15000], [-7000, 16000]]],
    #              [2, [[-2000, 28000], [1500, 30000], [1000, 33000], [-4000, 34000], [-8000, 31500], [-6500, 29000]]]]
    # target = [[[5000, 20000], [1, 2, 3], 60, 2], [[15000, 23000], [1, 2, 3], 70, 2], [[25000, 36000], [1, 2, 3], 40, 2],
    #           [[16000, 49000], [1, 2, 3], 60, 2], [[-2000, 41000], [1, 2, 3], 80, 2], [[32000, 58000], [1, 2, 3], 90, 2],
    #           [[-15000, 25000], [1, 2, 3], 80, 2]]
    # 47126算例数据
    # airport = [[[42000, -2000], 16, math.pi], [[38000, 30000], 60, 3 * math.pi / 4], [[54000, 15000], 16, math.pi / 2],
    #            [[-16000, 10000], 50, math.pi / 2]]
    # Uav = [[[42000, -2000], 1, 80, 0, 250], [[42000, -2000], 3, 60, 5, 220], [[38000, 30000], 3, 70, 5, 210],
    #        [[38000, 30000], 1, 80, 0, 240], [[54000, 15000], 2, 70, 3, 200, 3], [[54000, 15000], 3, 80, 4, 220],
    #        [[-16000, 10000], 2, 70, 2, 200]]
    #
    # obstacles = [[1, [[10000, 15000], 2000]], [1, [[15000, 35000], 5000]], [1, [[0, 53000], 3000]],
    #              [2, [[30000, 42000], [35000, 44000], [38000, 48000], [33000, 52000], [26000, 47000]]],
    #              [2, [[-8000, 11000], [-3000, 12000], [-2000, 15000], [-7000, 16000]]],
    #              [2, [[-2000, 28000], [1500, 30000], [1000, 33000], [-4000, 34000], [-8000, 31500], [-6500, 29000]]]]
    # target = [[[25000, 36000], [1, 2, 3], 40, 2], [[5000, 20000], [1, 2, 3], 60, 2], [[47500, 30000], [1, 2, 3], 40, 1],
    #           [[-2000, 41000], [1, 2, 3], 80, 2], [[16000, 49000], [1, 2, 3], 60, 2],
    #           [[15000, 5000], [1, 2, 3], 100, 1], [[40000, 18000], [1, 2, 3], 60, 1],
    #           [[47000, 52000], [1, 2, 3], 80, 2], [[30000, 19500], [1, 2, 3], 60, 1], [[30000, 2000], [1, 2, 3], 40, 1],
    #           [[32000, 58000], [1, 2, 3], 90, 2], [[15000, 23000], [1, 2, 3], 70, 2]]
    # 48166算例数据
    # airport = [[[42000, -2000], 16, math.pi], [[38000, 30000], 60, 3 * math.pi / 4], [[54000, 15000], 16, math.pi / 2],
    #            [[-16000, 10000], 50, math.pi / 2]]
    # Uav = [[[42000, -2000], 1, 80, 0, 250], [[42000, -2000], 3, 60, 5, 220], [[38000, 30000], 3, 70, 5, 210],
    #        [[38000, 30000], 1, 80, 0, 240], [[54000, 15000], 2, 70, 3, 200, 3], [[54000, 15000], 3, 80, 4, 220],
    #        [[-16000, 10000], 2, 70, 2, 200], [[-16000, 10000], 1, 80, 0, 250, 3]]
    #
    # obstacles = [[1, [[10000, 15000], 2000]], [1, [[15000, 35000], 5000]], [1, [[0, 53000], 3000]],
    #              [2, [[30000, 42000], [35000, 44000], [38000, 48000], [33000, 52000], [26000, 47000]]],
    #              [2, [[-8000, 11000], [-3000, 12000], [-2000, 15000], [-7000, 16000]]],
    #              [2, [[-2000, 28000], [1500, 30000], [1000, 33000], [-4000, 34000], [-8000, 31500], [-6500, 29000]]]]
    # target = [[[25000, 36000], [1, 2, 3], 40, 2], [[5000, 20000], [1, 2, 3], 60, 2], [[47500, 30000], [1, 2, 3], 40, 1],
    #           [[-2000, 41000], [1, 2, 3], 80, 2], [[20000, 15000], [1, 2, 3], 80, 1], [[5000, 66000], [1, 2, 3], 80, 2],
    #           [[16000, 49000], [1, 2, 3], 60, 2], [[15000, 5000], [1, 2, 3], 100, 1],
    #           [[40000, 18000], [1, 2, 3], 60, 1],
    #           [[47000, 52000], [1, 2, 3], 80, 2], [[30000, 19500], [1, 2, 3], 60, 1], [[30000, 2000], [1, 2, 3], 40, 1],
    #           [[32000, 58000], [1, 2, 3], 90, 2], [[-15000, 25000], [1, 2, 3], 80, 2],
    #           [[35000, 37000], [1, 2, 3], 60, 2], [[15000, 23000], [1, 2, 3], 70, 2]]
    targets = []
    uavs = []
    airports = []
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
    population_size = 50
    max_iter = 100
    threat_r = 2500
    optimal_chromosome, return_airport, _ = main(max_iter, population_size, uavs, targets, Obstacles, threat_r)
    # track_map(optimal_chromosome, uavs, targets, airports, Obstacles, return_airport)
