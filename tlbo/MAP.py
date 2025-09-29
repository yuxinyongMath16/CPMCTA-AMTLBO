# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2022年05月24日
"""
import math
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy

'''
障碍物种类分为圆形障碍'o'和多边形障碍'p'

'''


class Obstacle:
    def __init__(self, type, information):
        self.type = type
        self.information = information
        self.diameter = self.calculate_diameter()

    def calculate_diameter(self):
        if self.type == 'o':
            return 2 * self.information[1]
        else:
            return self.calculate_polygon_diameter(self.information)

    def calculate_polygon_diameter(self, information):
        diameter = 0
        for i in range(len(information)):
            for j in range(len(information) - i - 1):
                distance = math.sqrt((information[i][0] - information[j + i + 1][0]) ** 2 + (
                            information[i][1] - information[j + i + 1][1]) ** 2)
                if distance > diameter:
                    diameter = deepcopy(distance)
        return diameter


class Target:
    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value


class Map:
    '''
    地图类，存储地图的一些信息
    '''

    def __init__(self, x, y, obstacles, targets):
        self.x = x
        self.y = y
        self.obstacles = obstacles
        self.targets = targets

    def draw_circle(self, core, r):
        theta = np.arange(0, 2 * np.pi, 0.01)
        x = core[0] + r * np.cos(theta)
        y = core[1] + r * np.sin(theta)
        plt.plot(x, y, 'k')

    def draw_polygons(self, points):
        x = []
        y = []
        for point in points:
            x.append(point[0])
            y.append(point[1])
        x.append(x[0])
        y.append(y[0])
        plt.plot(x, y, 'k-')

    def represent_map(self):
        ''' Represents the map '''
        # Map representation
        # 绘制出地图
        plt.figure()
        for obs in self.obstacles:
            if obs.type == 'o':
                self.draw_circle(obs.information[0], obs.information[1])
            else:
                self.draw_polygons(obs.information)
        for target in self.targets:
            plt.plot(target.x, target.y, 'r*', markersize=7)
        plt.axis('equal')
        plt.show()
        plt.close()


if __name__ == '__main__':
    obstacles1 = [[1, [[10000, 15000], 2000]], [1, [[15000, 35000], 5000]], [1, [[45000, 25000], 1000]],
                 [1, [[30000, 15000], 2000]], [1, [[35000, 45000], 500]],
                 [2, [[30000, 20000], [35000, 23000], [40000, 31000], [33000, 35000], [21000, 30000]]]]
    targets1 = [[7500, 7500], 2], [[7500, 12500], 5], [[15000, 12500], 4], [[15000, 30000], 2], [[30000, 12500], 2], \
              [[30000, 30000], 3], [[45000, 12500], 3], [[45000, 30000], 2], [[47500, 30000], 2], [[5000, 20000], 3], \
              [[2500, 45000], 4], [[20000, 40000], 1], [[37500, 22500], 2], [[22500, 23500], 3], [[41500, 40000], 2], \
              [[25500, 3000], 3], [[35000, 34000], 2], [[25000, 36000], 2]
    obstacles = [[1, [[1000, 1500], 200]], [1, [[1500, 3500], 500]], [1, [[4500, 2500], 100]],
                 [1, [[3000, 1500], 200]], [1, [[3500, 4500], 150]], [1, [[5800, 3500], 200]],
                 [2, [[3000, 2500], [3500, 2700], [3800, 3100], [3300, 3500], [2600, 3000]]],
                 [2, [[1800, 2100], [2300, 2200], [2400, 2500], [1900, 2600]]],
                 [2, [[5800, 2000], [6150, 2200], [6100, 2500], [5600, 2600], [5200, 2350], [5350, 2100]]],
                 [2, [[4200, 4200], [5200, 4100], [4900, 4600], [4500, 4700]]]]
    targets = [[[2500, 3600], [1, 2, 3], 40], [[500, 2000], [1, 2, 3], 60], [[4750, 3000], [1, 2, 3], 40],
              [[250, 4100], [1, 2, 3], 80], [[2000, 1500], [1, 2, 3], 80], [[5800, 1800], [1, 2, 3], 80],
               [[1600, 4900], [1, 2, 3], 60], [[500, 500], [1, 2, 3], 100], [[4000, 1800], [1, 2, 3], 60],
               [[4700, 5200], [1, 2, 3], 80], [[3000, 1950], [1, 2, 3], 60], [[3000, 200], [1, 2, 3], 40],
               [[3200, 5800], [1, 2, 3], 90], [[6100, 4200], [1, 2, 3], 80], [[7000, 5200], [1, 2, 3], 90],
               [[6800, 3200], [1, 2, 3], 80], [[7100, 1800], [1, 2, 3], 80], [[7000, 1000], [1, 2, 3], 60],
               [[3500, 3700], [1, 2, 3], 60], [[1500, 2300], [1, 2, 3], 70]]
    Obstacles = []
    Targets = []
    for obstacle in obstacles:
        if obstacle[0] == 1:
            Obs = Obstacle('o', obstacle[1])
        else:
            Obs = Obstacle('p', obstacle[1])
        Obstacles.append(Obs)
    for target in targets:
        Tar = Target(target[0][0], target[0][1], target[1])
        Targets.append(Tar)
    map = Map(50000, 50000, Obstacles, Targets)
    # print(map.map)
    map.represent_map()
