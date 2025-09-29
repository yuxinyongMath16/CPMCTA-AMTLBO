# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2023年09月25日
"""
import math
import population_generation
import MAP
import imtlbo2


airport = [[[42000, 18000], 50, math.pi / 2], [[3000, 30000], 50, math.pi / 2], [[29000, 48000], 50, math.pi]]
Uav = [[[42000, 18000], 1, 80, 0, 250], [[42000, 18000], 3, 60, 5, 220], [[3000, 30000], 2, 70, 2, 200],
       [[29000, 48000], 1, 80, 0, 250, 3], [[29000, 48000], 2, 70, 3, 200, 3]]

obstacles = [[1, [[10000, 15000], 2000]], [1, [[15000, 35000], 5000]], [1, [[45000, 25000], 1000]],
             [1, [[30000, 15000], 2000]], [1, [[35000, 45000], 500]],
             [2, [[30000, 25000], [35000, 27000], [38000, 31000], [33000, 35000], [26000, 30000]]],
             [2, [[18000, 21000], [23000, 22000], [24000, 25000], [19000, 26000]]]]
target = [[[25000, 36000], [1, 2, 3], 40], [[5000, 20000], [1, 2, 3], 60], [[47500, 30000], [1, 2, 3], 40],
          [[2500, 45000], [1, 2, 3], 80], [[20000, 15000], [1, 2, 3], 80]]
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
max_iter = 300
tea_num = 4

iteration_optimal_set = []
run_time_set = []
for i in range(10):
    optimal_chromosome, iteration_optimal_value, run_time = imtlbo2.main(max_iter, population_size, uavs, targets, Obstacles, tea_num)
    iteration_optimal_set.append(iteration_optimal_value)
    run_time_set.append(run_time)

print('迭代最优值集合', iteration_optimal_set)
print('迭代时间集合', run_time_set)