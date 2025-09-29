# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2023年07月23日
tlbo主程序
"""
import voyage_estimate
import time
import math
import MAP
import numpy as np
import population_generation
import population_generation_fix
import fitness_calculation
import population_update
import matplotlib
matplotlib.use('agg')
import matplotlib.pyplot as plt


def main(max_iter, population_size, uavs, targets, Obstacles, threat_r):
    start = time.time()
    move_air_time = []
    iteration_optimal_value = []
    iteration_optimal_f1 = []
    iteration_optimal_f2 = []
    # 程序初始化
    solutions, resources = population_generation_fix.fixed_population_new11_1()
    iter_num = 0
    while True:
        if iter_num < 1:
            pop_fitness, time_sum, return_airports, pop_f1, pop_f2 = fitness_calculation.fitness(solutions, targets, uavs, Obstacles, threat_r)
        iter_num = iter_num + 1
        if iter_num > max_iter:
            break
        print('迭代次数：', iter_num)
        print('此代计算移动机场号是', time_sum)
        move_air_time.append(time_sum)
        if iter_num % 10 == 0 or iter_num == 1:
            optimal_value1 = min(pop_fitness)
            iteration_optimal_value.append(optimal_value1)
            optimal_index_iter = pop_fitness.index(min(pop_fitness))
            optimal_f1 = pop_f1[optimal_index_iter]
            optimal_f2 = pop_f2[optimal_index_iter]
            iteration_optimal_f1.append(optimal_f1)
            iteration_optimal_f2.append(optimal_f2)
            print('最优值是', optimal_value1)

        solutions, pop_fitness, pop_f1, pop_f2 = population_update.population_update(solutions, uavs, targets, pop_fitness, Obstacles, threat_r, pop_f1, pop_f2)
    pop_fitness, time_sum, return_airports, pop_f1, pop_f2 = fitness_calculation.fitness(solutions, targets,
                                                                                                 uavs, Obstacles,
                                                                                                 threat_r)
    optimal_value = min(pop_fitness)
    optimal_index = pop_fitness.index(optimal_value)
    # optimal_indicator1 = indicator1[optimal_index]
    # optimal_indicator2 = indicator2[optimal_index]
    # print('最优值是：', optimal_value)
    optimal_solution = solutions[optimal_index]
    optimal_solution_airport = return_airports[optimal_index]
    print('最优方案为：', optimal_solution)
    print('最优方案的机场', optimal_solution_airport)
    print('最优值', optimal_value)
    # print('最优指标1', optimal_indicator1)
    # print('最优指标2', optimal_indicator2)
    # print('适应度值', pop_fitness)
    # print('指标1', indicator1)
    # print('指标2', indicator2)
    end = time.time()
    run_time = end - start
    print("Runtime is ：", run_time)  # 计时结果！！！
    # print('程序计算移动机场总耗时是', sum(move_air_time))
    return optimal_solution, iteration_optimal_value, run_time, iteration_optimal_f1, iteration_optimal_f2


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
