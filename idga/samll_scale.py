# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2022年09月20日
"""
import task_assignment
import chromosome_generation
import MAP
import math
import draw_digital_map
import generate_animation


# Uav = [[[4300, 1800], 1, 80, 0, 250], [[4300, 1800], 3, 60, 5, 220], [[4300, 1800], 2, 70, 2, 200],
#        [[4300, 1800], 1, 80, 0, 250], [[4300, 1800], 2, 90, 3, 200], [[4300, 1800], 3, 80, 4, 220],
#        [[4300, 1800], 3, 70, 5, 210], [[4300, 1800], 1, 80, 0, 240], [[4300, 1800], 2, 90, 3, 220],
#        [[4300, 1800], 2, 70, 2, 200]]
# obstacles = [[1, [[1000, 1500], 200]], [1, [[1500, 3500], 500]], [1, [[4500, 2500], 100]],
#              [1, [[3000, 1500], 200]], [1, [[3500, 4500], 150]], [1, [[5800, 3500], 200]],
#              [2, [[3000, 2500], [3500, 2700], [3800, 3100], [3300, 3500], [2600, 3000]]],
#              [2, [[1800, 2100], [2300, 2200], [2400, 2500], [1900, 2600]]],
#              [2, [[5800, 2000], [6150, 2200], [6100, 2500], [5600, 2600], [5200, 2350], [5350, 2100]]],
#              [2, [[4200, 4200], [5200, 4100], [4900, 4600], [4500, 4700]]]]
# target = [[[2500, 3600], [1, 2, 3], 40], [[500, 2000], [1, 2, 3], 60], [[4750, 3000], [1, 2, 3], 40],
#            [[250, 4100], [1, 2, 3], 80], [[2000, 1500], [1, 2, 3], 80], [[5800, 1800], [1, 2, 3], 80],
#            [[1600, 4900], [1, 2, 3], 60], [[500, 500], [1, 2, 3], 100], [[4000, 1800], [1, 2, 3], 60],
#            [[4700, 5200], [1, 2, 3], 80], [[3000, 1950], [1, 2, 3], 60], [[3000, 200], [1, 2, 3], 40],
#            [[3200, 5800], [1, 2, 3], 90], [[6100, 4200], [1, 2, 3], 80], [[7000, 5200], [1, 2, 3], 90],
#            [[6800, 3200], [1, 2, 3], 80], [[7100, 1900], [1, 2, 3], 80], [[7000, 1000], [1, 2, 3], 60],
#            [[3500, 3700], [1, 2, 3], 60], [[0, 3000], [1, 2, 3], 90]]
airport = [[[42000, 18000], 50, math.pi/2], [[3000, 30000], 50, math.pi /2], [[29000, 48000], 50, math.pi]]
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
    c_air = chromosome_generation.Airport(i + 1, airport[i][0], airport[i][1], airport[i][2])
    airports.append(c_air)
for i in range(len(target)):
    c_tar = chromosome_generation.Target(i + 1, target[i][0], target[i][1], target[i][2])
    targets.append(c_tar)
for i in range(len(Uav)):
    c_uav = chromosome_generation.UAV(i + 1, Uav[i][0], Uav[i][1], Uav[i][2], Uav[i][3], Uav[i][4], airports)
    uavs.append(c_uav)
for obstacle in obstacles:
    if obstacle[0] == 1:
        Obs = MAP.Obstacle('o', obstacle[1])
    else:
        Obs = MAP.Obstacle('p', obstacle[1])
    Obstacles.append(Obs)
population = 150
Ne = 60
Ncr = 48
Nm = 48
iter_num = 100
optimal_chromosome, return_airport, optimal_value = task_assignment.main(targets, uavs, Obstacles, population, iter_num, Ne, Ncr, Nm)
# draw_digital_map.track_map(optimal_chromosome, uavs, targets, airports, Obstacles, return_airport)
# generate_animation.track_map(optimal_chromosome, uavs, targets, airports, Obstacles, return_airport, optimal_value)