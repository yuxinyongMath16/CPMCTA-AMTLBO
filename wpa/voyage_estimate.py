# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2022年05月25日
可视图路径规划
"""

import math
import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import segment_intersection
from MAP import Obstacle, Target, Map

'''
第一部分，各种类函数
1、直线类（用于判断直线是否穿过障碍，多边形的‘切线’）
2、节点类（用于生成路径）
3、切线类（用于产生圆的切线）
'''


class Line:
    def __init__(self, position1, position2):
        self.star_position = position1
        self.end_position = position2
        self.k = self.calculate_slope(self.star_position, self.end_position)
        self.b = self.calculate_constant(self.k, self.star_position)

    def calculate_slope(self, position1, position2):
        if position2[0] - position1[0] == 0:
            k = 'none'
        else:
            delta_x = position2[0] - position1[0]
            delta_y = position2[1] - position1[1]
            k = delta_y / delta_x
        return k

    def calculate_constant(self, k, position1):
        """
        :param k: 斜率
        :param position1: 一个点坐标
        :return: 直线方程的常数参数
        """
        if k == 'none':
            b = 'none'
        else:
            b = position1[1] - k * position1[0]
        return b


class Note:
    def __init__(self, position):
        self.position = position
        self.previous_node = []
        self.back_node = []

    def find_previous_node(self, node):
        for p_node in self.previous_node:
            if node.position == p_node.position:
                return True
        return False

    def find_back_node(self, node):
        for b_node in self.back_node:
            if node.position == b_node.position:
                return True
        return False

    def add_previous_node(self, node):
        if not self.find_previous_node(node):
            self.previous_node.append(node)

    def add_back_node(self, node):
        if not self.find_back_node(node):
            self.back_node.append(node)


class Tangent:
    def __init__(self, k, b, x0, y0):
        self.k = k
        self.b = b
        self.x0 = x0
        self.y0 = y0


'''
第2部分，统计一条直线上的障碍数量
'''


# 点到点的距离
def distance_point_point(point1, point2):
    distance = math.sqrt((point1[0]-point2[0])**2 + (point1[1]-point2[1])**2)
    return distance


# 点到直线距离,line是直线类，point是2*1列表
def distance_line_point(line, point):
    if line.k == 'none':
        distance = abs(point[0] - line.star_position[0])
    else:
        distance = abs(line.k * point[0] - point[1] + line.b) / math.sqrt(line.k ** 2 + 1)
    return distance


# 此处用于计算切线时候的判断，包含等于
def out_of_range_judgement1(point1, point2, point):
    judgement = 0
    # point在point1和point2构成的矩形之中，judgement = 0，否则等于1
    if point[0] <= point1[0] and point[0] <= point2[0]:
        judgement = 1
    elif point[0] >= point1[0] and point[0] >= point2[0]:
        judgement = 1
    elif point[1] <= point1[1] and point[1] <= point2[1]:
        judgement = 1
    elif point[1] >= point1[1] and point[1] >= point2[1]:
        judgement = 1
    return judgement


# 判断圆形障碍是否在线段范围内,[点]，[点]，[[圆心]，半径]
def out_of_range(point1, point2, circle):
    if point2[0] > point1[0]:
        star_x = point1[0] - math.sqrt(2)/2*circle[1]
        end_x = point2[0] + math.sqrt(2)/2*circle[1]
    else:
        star_x = point2[0] - math.sqrt(2) / 2 * circle[1]
        end_x = point1[0] + math.sqrt(2) / 2 * circle[1]
    if point2[1] > point1[1]:
        star_y = point1[1] - math.sqrt(2)/2*circle[1]
        end_y = point2[1] + math.sqrt(2) / 2 * circle[1]
    else:
        star_y = point2[1] - math.sqrt(2) / 2 * circle[1]
        end_y = point1[1] + math.sqrt(2) / 2 * circle[1]
    if star_x <= circle[0][0] <= end_x and star_y <= circle[0][1] <= end_y:
        return False
    return True


# 判断路径是否经过圆形障碍，直线类，障碍类，[点]，[点]
def circle_obstacle_judgment(line, o_obstacle, point1, point2):
    distance = distance_line_point(line, o_obstacle.information[0])
    if distance < (o_obstacle.diameter / 2) - 1 and not out_of_range(point1, point2, o_obstacle.information):
        return True
    else:
        return False


# 判断两点是否在直线的两边(直线是否穿过多边的子程序),[点]，[点]，直线类
def point_both_sides_line(point1, point2, line):
    computer_error = 0.001
    if line.k != 'none':
        # 等于0的情况意味着直线穿过点或者一条边，这种情况是允许的
        if (line.k * point1[0])+line.b-point1[1] > computer_error and (line.k * point2[0])+line.b-point2[1] < -computer_error:
            # print('点一在直线的下方，点二在直线的上方')
            return True
        elif (line.k * point1[0])+line.b-point1[1] < -computer_error and (line.k * point2[0])+line.b-point2[1] > computer_error:
            # print('点一在直线的上方，点二在直线的下方')
            return True
    else:
        if point1[0] > line.star_position[0] > point2[0]:
            # print('点一在直线的右边，点二在直线的左边')
            return True
        elif point1[0] < line.star_position[0] < point2[0]:
            # print('点一在直线的左边边，点二在直线的右边')
            return True
    # print('两点在直线同侧')
    return False


# 直线是否穿过多边形(多边形障碍判断子程序1)，直线类，多边形障碍物类
def line_through_polygon(line, p_obstacle):
    # print('障碍物信息', p_obstacle.information)
    for i in range(len(p_obstacle.information)-1):
        for j in range(len(p_obstacle.information)-i-1):
            # print('第一个点', p_obstacle.information[i], '第二个点', p_obstacle.information[j+i+1])
            # print('k:', line.k, 'b:', line.b)
            if point_both_sides_line(p_obstacle.information[i], p_obstacle.information[j+i+1], line):
                return True
    return False


# 线段是否与多边形有交点(多边形障碍判断子程序2)，[点]，[[点]，[点]，...[点]]
def line_intersection_polygon(line_point, polygon):
    points_polygon = deepcopy(polygon)
    points_polygon.append(points_polygon[0])
    for i in range(len(points_polygon)-1):
        res = segment_intersection.__intersect(line_point[0], line_point[1], points_polygon[i], points_polygon[i+1])
        if res:
            return True
    return False


# 线段是否越过多边形(主程序)(线段上的障碍物子程序2)，直线类，障碍类
def line_segment_through_polygon(line, polygon):
    # print('直线穿过多边形', line_through_polygon(line, polygon))
    # print('线段穿过多边形', line_intersection_polygon([line.star_position, line.end_position], polygon.information))
    if line_through_polygon(line, polygon) and line_intersection_polygon([line.star_position, line.end_position], polygon.information):
        return True
    return False


# 点到障碍物的最小距离(排序障碍物的子程序)
def min_point_obstacle(point, obstacle):
    min_distance = 50000
    if obstacle.type == 'o':
        min_distance = distance_point_point(point, obstacle.information[0]) - obstacle.information[1]
    else:
        for point1 in obstacle.information:
            distance = distance_point_point(point, point1)
            if distance < min_distance:
                min_distance = deepcopy(distance)
    return min_distance


# 障碍物排序(多边形障碍判断子程序3)
def obstacle_sort(point, obstacles):
    if len(obstacles) > 1:
        sort_obstacles = []
        min_distances = []
        for obstacle in obstacles:
            min_distance = min_point_obstacle(point, obstacle)
            min_distances.append(min_distance)
        index = np.argsort(min_distances)
        for i in index:
            sort_obstacles.append(obstacles[i])
        return sort_obstacles
    return obstacles


# 第二部分主函数统计路径上的障碍物
def statistic_obstacles(point1, point2, obstacles):
    line = Line(point1, point2)
    obstacle_in_path = []
    for obstacle in obstacles:
        if obstacle.type == 'o':
            if circle_obstacle_judgment(line, obstacle, point1, point2):
                obstacle_in_path.append(obstacle)
        else:
            if line_segment_through_polygon(line, obstacle):
                obstacle_in_path.append(obstacle)
    obstacle_in_path = obstacle_sort(point1, obstacle_in_path)
    return obstacle_in_path


'''
第3部分，计算越过障碍时的，中间节点
'''


# 计算切线的参数
def calculate_tangent_parameter(point, par_a, par_b):
    k = -par_a / par_b
    b = (par_a*point[0] + par_b*point[1]) / par_b
    return k, b


# 圆的切线计算
def calculate_circle_tangent(point, core, radius):
    k1, b1, k2, b2 = 'none', 'none', 'none', 'none'
    m1 = (core[0] - point[0])**2 - radius**2
    m2 = (core[1] - point[1])**2 - radius**2
    m3 = (core[0] - point[0])*(core[1] - point[1])
    # print(m1, m2, m3)
    if m1 != 0:
        par_a1 = (-m3 + math.sqrt(m3**2-m1*m2))/m1
        par_a2 = (-m3 - math.sqrt(m3**2-m1*m2))/m1
        par_b = 1
        k1, b1 = calculate_tangent_parameter(point, par_a1, par_b)
        k2, b2 = calculate_tangent_parameter(point, par_a2, par_b)
    elif m1 == 0 and m2 != 0:
        par_a = 1
        par_b1 = (-m3 + abs(m3))/m2
        par_b2 = (-m3 - abs(m3))/m2
        if par_b1 != 0:
            k1, b1 = calculate_tangent_parameter(point, par_a, par_b1)
        else:
            k1, b1 = 'none', 'none'
        if par_b2 != 0:
            k2, b2 = calculate_tangent_parameter(point, par_a, par_b2)
        else:
            k2, b2 = 'none', 'none'
    elif m1 == m2 == 0:
        k1, b1, k2, b2 = 0, point[1], 'none', 'none'
    tangent1 = Tangent(k1, b1, point[0], point[1])
    tangent2 = Tangent(k2, b2, point[0], point[1])
    return [tangent1, tangent2]


# 圆的切线类转为直线类, (只有第二段切线需要转化)
def tangent_transform_line(tangent, mid_point):
    line = (mid_point, [tangent.x0, tangent.y0])
    return line


# 多边行‘切线’计算
def calculate_polygon_tangent(point, p_obstacle):
    # 包含直线和起点或者终点
    polygon_info = p_obstacle.information
    lines = []
    for point1 in polygon_info:
        line = Line(point, point1)
        if not line_segment_through_polygon(line, p_obstacle):
            lines.append([line, point1])
    return lines


# 多边形中间点判断1（两直线相交的情况）
def polygon_mid_point_judgement1(line1, line2):
    if line1[1] == line2[1]:
        return [line1[1]]
    else:
        return 'none'


# 计算多边形的边
def calculate_polygon_side(polygon_info):
    points = deepcopy(polygon_info)
    points.append(polygon_info[0])
    sides = []
    for i in range(len(points)-1):
        side = distance_point_point(points[i], points[i+1])
        sides.append(side)
    return sides


# 多边形中间点计算2（两直线不相交）
def polygon_mid_point_judgement2(line1, line2, midpoint1, midpoint2, sides):
    if line1[1] != line2[1] and line1[1] not in midpoint2 and line2[1] not in midpoint1:
        distance = distance_point_point(line1[1], line2[1])
        if distance in sides:
            return [line1[1], line2[1]]
    return 'none'


# 多边形中间点计算...修改
def polygon_mid_point_judgement_xx(point1, point2, line1, line2, sides):
    mid_points = []
    if line1[1] != line2[1]:
        distance = distance_point_point(line1[1], line2[1])
        if distance in sides:
            mid_points.append([line1[1], line2[1], distance])
    compare_distance = []
    if len(mid_points) > 1:
        for mid in mid_points:
            distance1 = distance_point_point(point1, line1[1])
            distance2 = distance_point_point(line1[2], point2)
    return 'none'


# 多边形路径中间点，[[[点],[点]], [线]]
def polygon_path(point1, point2, p_obstacle):
    mid_points = []
    polygon_info = p_obstacle.information
    lines1 = calculate_polygon_tangent(point1, p_obstacle)
    lines2 = calculate_polygon_tangent(point2, p_obstacle)
    midpoint1 = midpoint_extraction(lines1)
    midpoint2 = midpoint_extraction(lines2)
    sides = calculate_polygon_side(polygon_info)
    for i in range(len(lines1)):
        for j in range(len(lines2)):
            mid_point_judgement1 = polygon_mid_point_judgement1(lines1[i], lines2[j])
            if mid_point_judgement1 != 'none':
                mid_points.append([mid_point_judgement1, lines2[0]])
            mid_points_judgement2 = polygon_mid_point_judgement2(lines1[i], lines2[j], midpoint1, midpoint2, sides)
            if mid_points_judgement2 != 'none':
                # [点， 线]
                mid_points.append([mid_points_judgement2, lines2[0]])
    return mid_points


def midpoint_extraction(line):
    midpoint = []
    for element in line:
        midpoint.append(element[1])
    return midpoint


def judge_same_set(point, midpoint):
    for element in midpoint:
        if element == point:
            return False
    return True


# 计算两条切线的交点，即为中间点
def calculate_tangent_intersection(tangent1, tangent2, circle):
    mid_point = []
    if tangent1.k == 0 and tangent2.k != 0 and tangent2.k != 'none':
        mid_point_y = tangent1.y0
        mid_point_x = (mid_point_y - tangent2.b) / tangent2.k
        mid_point.append([mid_point_x, mid_point_y])
    elif tangent1.k == 'none' and tangent2.k != 0 and tangent2.k != 'none':
        mid_point_x = tangent1.x0
        mid_point_y = tangent2.k * mid_point_x + tangent2.b
        mid_point.append([mid_point_x, mid_point_y])
    elif tangent1.k == 0 and tangent2.k == 'none':
        mid_point.append([tangent2.x0, tangent1.y0])
    elif tangent1.k == 'none' and tangent2.k == 0:
        mid_point.append([tangent1.x0, tangent2.y0])
    elif tangent1.k != 'none' and tangent1.k != 0 and tangent2.k == 0:
        mid_point_y = tangent2.y0
        mid_point_x = (mid_point_y - tangent1.b) / tangent1.k
        mid_point.append([mid_point_x, mid_point_y])
    elif tangent1.k != 'none' and tangent1.k != 0 and tangent2.k == 'none':
        mid_point_x = tangent2.x0
        mid_point_y = tangent1.k * mid_point_x + tangent1.b
        mid_point.append([mid_point_x, mid_point_y])
    elif tangent1.k != 'none' and tangent1.k != 0 and tangent2.k != 0 and tangent2.k != 'none':
        if tangent1.k - tangent2.k == 0:
            print('直线信息', tangent1.k, tangent2.k, tangent1.b, tangent2.b)
            return 'none'
        else:
            mid_point_x = (tangent2.b - tangent1.b) / (tangent1.k - tangent2.k)
            mid_point_y = tangent2.k * mid_point_x + tangent2.b
            mid_point.append([mid_point_x, mid_point_y])
    for point in mid_point:
        if distance_point_point(point, circle[0]) > 2*circle[1]:
            mid_point.remove(point)
    if len(mid_point) != 0:
        return mid_point
    return 'none'


# 圆形路径中间点，[[[点]], [线]]
def circle_path(point1, point2, circle):
    tangents1 = calculate_circle_tangent(point1, circle[0], circle[1])
    tangents2 = calculate_circle_tangent(point2, circle[0], circle[1])
    mid_points = []
    for i in range(len(tangents1)):
        for j in range(len(tangents2)):
            intersections = calculate_tangent_intersection(tangents1[i], tangents2[j], circle)
            if intersections != 'none':
                line = tangent_transform_line(tangents2[j], intersections[0])
                mid_points.append([intersections, line])
    return mid_points


'''
第4部分，生成预估航程及轨迹
'''


def increase_note(nodes, add_position):
    for node in nodes:
        if node.position == add_position:
            find_node = node
            # 如果节点集合有增加的节点，则返回集合和找到的节点
            return nodes, find_node
    add_node = Note(add_position)
    nodes.append(add_node)
    # 如果节点集合没有增加的节点，则返回增加节点后的节点集合和增加的节点
    return nodes, add_node


def update_previous_back_node(nodes, previous_position, act_node):
    for node in nodes:
        if node.position == previous_position:
            node.add_back_node(act_node)
            act_node.add_previous_node(node)
    return nodes


def mid_to_next_impact_check(star_position, next_position, obstacles):
    line = Line(star_position, next_position)
    obstacle_in_path = []
    for obstacle in obstacles:
        if obstacle.type == 'o':
            if circle_obstacle_judgment(line, obstacle, star_position, next_position):
                obstacle_in_path.append(obstacle)
        else:
            if line_segment_through_polygon(line, obstacle):
                obstacle_in_path.append(obstacle)
    if len(obstacle_in_path) != 0:
        return True
    return False


def estimate_track(star_position, end_position, obstacles, nodes):
    actual_position = deepcopy(star_position)
    obstacles_in_path = statistic_obstacles(actual_position, end_position, obstacles)
    output_obstacles_in_path = deepcopy(obstacles_in_path)
    # print('途径的障碍物', obstacles_in_path)
    if len(obstacles_in_path) == 0:
        next_position = deepcopy(end_position)
        # print('起点是输入的起点节点', actual_position, '下个点就是终点', next_position)
        nodes, add_node = increase_note(nodes, next_position)
        nodes = update_previous_back_node(nodes, actual_position, add_node)
        return
    else:
        the_first_obstacles = obstacles_in_path[0].type
        if obstacles_in_path[0].type == 'o':
            mid_points = circle_path(actual_position, end_position, obstacles_in_path[0].information)
            # print('途径的第一个障碍是圆形障碍，中点是', mid_points)
        else:
            mid_points = polygon_path(actual_position, end_position, obstacles_in_path[0])
            # print('途径的第一个障碍是多边形障碍，中点是', mid_points)
            # print('中间点', mid_points)
        for i in range(len(mid_points)):
            actual_position = deepcopy(star_position)
            judgement = 1
            for j in range(len(mid_points[i][0])):
                next_position =deepcopy(mid_points[i][0][j])
                if j == 0:
                    if mid_to_next_impact_check(actual_position, next_position, obstacles):
                        # print('该线段将要穿越障碍物')
                        judgement = 0
                        break
                    # else:
                        # print('不穿过障碍物，继续运行')
                nodes, add_node = increase_note(nodes, next_position)
                nodes = update_previous_back_node(nodes, actual_position, add_node)
                actual_position = deepcopy(next_position)
            if judgement == 1:
                estimate_track(actual_position, end_position, obstacles, nodes)
    return output_obstacles_in_path


def generate_path(star_point, end_point, obstacles):
    star_node = Note(star_point)
    nodes = [star_node]
    obstacles_in_path = estimate_track(star_point, end_point, obstacles, nodes)
    # print(nodes)
    paths = node_transform_path(nodes, star_point, end_point)
    new_paths = eliminate_unreasonable_midpoints(paths, obstacles_in_path)
    # print(new_paths)
    # print('obstacles_in_path', obstacles_in_path)
    return new_paths


def eliminate_useless_points(path_list, obstacles_in_path):
    # print(path_list)
    new_path_list = path_list
    while True:
        end_for = False
        for i in range(len(path_list)):
            for j in range(len(path_list)-1-1-i):
                actual_position = path_list[i]
                end_position = path_list[len(path_list)-1-j]
                segment_obstacles_in_path = statistic_obstacles(actual_position, end_position, obstacles_in_path)
                if len(segment_obstacles_in_path) == 0:
                    new_path_list = []
                    for p in range(i+1):
                        # print('索引i+1', i+1, p)
                        # print('正向记录点', path_list[p])
                        new_path_list.append(path_list[p])
                    for q in range(j+1):
                        # print('索引i=j+1', j + 1, q, len(path_list)-(j+1)+q)
                        # print('逆向记录点', path_list[len(path_list)-(j+1)+q])
                        new_path_list.append(path_list[len(path_list)-(j+1)+q])
                    end_for = True
                    break
            if end_for:
                break
        if path_list == new_path_list:
            break
        path_list = new_path_list
    return new_path_list


def eliminate_unreasonable_midpoints(paths, obstacles_in_path):
    new_paths_list = []
    for path_list in paths:
        new_path_list = eliminate_useless_points(path_list, obstacles_in_path)
        new_paths_list.append(new_path_list)
    return new_paths_list


def optimal_path_generate(star_point, end_point, obstacles):
    if star_point == end_point:
        return 0, []
    star_node = Note(star_point)
    nodes = [star_node]
    obstacles_in_path = estimate_track(star_point, end_point, obstacles, nodes)
    paths = node_transform_path(nodes, star_point, end_point)
    new_paths = eliminate_unreasonable_midpoints(paths, obstacles_in_path)
    paths_length = []
    for path in new_paths:
        path_length = 0
        for i in range(len(path)-1):
            path_length += distance_point_point(path[i+1], path[i])
        paths_length.append(path_length)
    if len(paths_length) == 0:
        return distance_point_point(star_point, end_point) * 5, []
    else:
        optimal_distance = min(paths_length)
        optimal_path = new_paths[paths_length.index(optimal_distance)]
        return optimal_distance, [optimal_path]


def node_transform_path(nodes, star_point, end_point):
    paths = []
    number = 1
    # for node in nodes:
    #     print('nodes节点位置：', number, node.position, '节点前向信息', [p_node.position for p_node in node.previous_node],
    #           '节点后向信息', [b_node.position for b_node in node.back_node])
    #     number += 1
    # node_show(nodes)
    for node in nodes:
        for back_node in node.back_node:
            if back_node.position == end_point:
                paths.append([end_point, node.position])
                break
    for path in paths:
        act_node = path[-1]
        while act_node != star_point:
            for node in nodes:
                for back_node in node.back_node:
                    if back_node.position == act_node:
                        path.append(node.position)
                        break
            act_node = path[-1]
    for path in paths:
        path.reverse()
    # print('可行路径', paths)
    return paths


def path_transform(path):
    path_x = []
    path_y = []
    for pa in path:
        path_x.append(pa[0])
        path_y.append(pa[1])
    return [path_x, path_y]


def draw_track_picture(map, paths):
    plt.figure()
    for obs in map.obstacles:
        if obs.type == 'o':
            map.draw_circle(obs.information[0], obs.information[1])
        else:
            map.draw_polygons(obs.information)
    for target in map.targets:
        plt.plot(target.x, target.y, 'r*', markersize=7)
    for path in paths:
        path_draw = path_transform(path)
        plt.plot(path_draw[0], path_draw[1], 'b-')
    plt.axis('equal')
    plt.show()

'''
debug函数
'''


def node_show(nodes):
    node_list = []
    for node in nodes:
        back_list = []
        previous_list = []
        for back_node in node.back_node:
            back_list.append(back_node.position)
        for previous_node in node.previous_node:
            previous_list.append(previous_node.position)
        node_list.append([node.position, previous_list, back_list])
    print(node_list)


if __name__ == '__main__':
    # obstacles = [[1, [[10000, 15000], 2000]], [1, [[15000, 35000], 5000]], [1, [[45000, 25000], 1000]],
    #              [1, [[30000, 15000], 2000]], [1, [[35000, 45000], 500]],
    #              [2, [[30000, 20000], [35000, 23000], [40000, 31000], [33000, 35000], [21000, 30000]]]]
    # obstacles1 = [[1, [[10000, 15000], 2000]], [1, [[15000, 35000], 5000]], [1, [[45000, 25000], 1000]],
    #              [1, [[30000, 15000], 2000]], [1, [[35000, 45000], 500]]]
    # targets = [[7500, 7500], 2], [[7500, 12500], 5], [[15000, 12500], 4], [[15000, 30000], 2], [[30000, 12500], 2], \
    #           [[30000, 30000], 3], [[45000, 12500], 3], [[45000, 30000], 2], [[47500, 30000], 2], [[5000, 20000], 3], \
    #           [[2500, 45000], 4], [[20000, 40000], 1], [[37500, 22500], 2], [[22500, 23500], 3], [[41500, 40000], 2], \
    #           [[25500, 3000], 3], [[35000, 34000], 2], [[25000, 36000], 2]
    obstacles2 = [[1, [[1000, 1500], 200]], [1, [[1500, 3500], 500]], [1, [[4500, 2500], 100]],
                 [1, [[3000, 1500], 200]], [1, [[3500, 4500], 50]],
                 [2, [[3000, 2500], [3500, 2700], [3800, 3100], [3300, 3500], [2600, 3000]]],
                 [2, [[1800, 2100], [2300, 2200], [2400, 2500], [1900, 2600]]]]
    targets1 = [[[25000, 36000], 40], [[50000, 20000], 60], [[47500, 30000], 40],
              [[2500, 45000], 80], [[20000, 15000], 80]]
    obstacles = [[1, [[1000, 1500], 200]], [1, [[1500, 3500], 500]], [1, [[0, 5300], 300]],
                 [2, [[3000, 4200], [3500, 4400], [3800, 4800], [3300, 5200], [2600, 4700]]],
                 [2, [[-800, 1100], [-300, 1200], [-200, 1500], [-700, 1600]]],
                 [2, [[-200, 2800], [150, 3000], [100, 3300], [-400, 3400], [-800, 3150], [-650, 2900]]]]
    obstacles1 = [[1, [[1000, 1500], 200]], [1, [[1500, 3500], 500]], [1, [[4500, 2500], 100]],
                 [1, [[3000, 1500], 200]], [1, [[3500, 4500], 150]], [1, [[5800, 3500], 200]],
                 [2, [[3000, 2500], [3500, 2700], [3800, 3100], [3300, 3500], [2600, 3000]]],
                 [2, [[1800, 2100], [2300, 2200], [2400, 2500], [1900, 2600]]],
                 [2, [[5800, 2000], [6150, 2200], [6100, 2500], [5600, 2600], [5200, 2350], [5350, 2100]]],
                 [2, [[4200, 4200], [5200, 4100], [4900, 4600], [4500, 4700]]]]
    targets = [[[2500, 3600], [1, 2, 3], 40], [[500, 2000], [1, 2, 3], 60], [[4750, 3000], [1, 2, 3], 40],
              [[250, 4500], [1, 2, 3], 80], [[2000, 1500], [1, 2, 3], 80], [[5800, 1800], [1, 2, 3], 80],
              [[1600, 4900], [1, 2, 3], 60], [[500, 500], [1, 2, 3], 100], [[4000, 1800], [1, 2, 3], 60],
              [[4700, 5200], [1, 2, 3], 80], [[3000, 1950], [1, 2, 3], 60], [[3000, 200], [1, 2, 3], 40],
              [[3200, 5800], [1, 2, 3], 90], [[6100, 4200], [1, 2, 3], 80], [[7000, 5200], [1, 2, 3], 90],
              [[6800, 3200], [1, 2, 3], 80], [[7100, 2200], [1, 2, 3], 80], [[7000, 1000], [1, 2, 3], 60],
              [[3500, 3700], [1, 2, 3], 60], [[1500, 2300], [1, 2, 3], 70], [[300, 7444], [1, 2, 3], 70],
               [[4300, 2461], [1, 2, 3], 70], [[300, 7721], [1, 2, 3], 80]]
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
    # 无问题
    star_point = [1000, 1250]
    end_point = [1100, 1800]
    # 报错，
    star_point1 = [2000, 1500]
    end_point1 = [300.0000000000003, 7444.121567173532]
    # 无问题，计算机误差带来的错误
    star_point01 = [2000, 1500]
    end_point01 = [300, 7444]
    # 死循环，，%%%%已解决
    star_point2 = [500, 2000]
    end_point2 = [4300, 2461]
    # 报错， 无问题，计算机误差带来的错误
    star_point3 = [2000, 1500]
    end_point3 = [300, 7721]
    # 无问题，计算机误差带来的错误
    star_point4 = [1800, 2100]
    end_point4 = [300, 7721]
    # 中间点没有用问题
    star_point5 = [4700, 5200]
    end_point5 = [-1500, 2500]

    points_path = generate_path(star_point5, end_point5, Obstacles)

    # opt_distance, points_path = optimal_path_generate(star_point2, end_point2, Obstacles)
    # print('最优距离是', opt_distance)
    # points_path = single_estimate_track(star_point, end_point, Obstacles)

    print('路径为', points_path)
    draw_track_picture(map, points_path)

    # obstacles_in_path = statistic_obstacles(star_point4, end_point4, Obstacles)
    # for ob in obstacles_in_path:
    #     print(ob.information)