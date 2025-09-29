# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2023年08月25日
"""
import numpy as np


def calculate_survival_target_points(task_time, target_attack_time, targets):
    survival_target = []
    for i in range(len(target_attack_time)):
        if target_attack_time[i][1] > task_time:
            survival_target.append(targets[target_attack_time[i][0] - 1].position)
    return survival_target


# 通过三角形面积法计算点到直线距离
def threat_function(line_point1, line_point2, point_list, threat_r):
    penalty_distance_set = []
    for tar_position in point_list:
        if tar_position != line_point1 and tar_position != line_point2:
            point = tar_position
            vec1 = [line_point1[0] - point[0], line_point1[1] - point[1]]
            vec2 = [line_point2[0] - point[0], line_point2[1] - point[1]]
            # 面积/底边 = 高
            distance = np.abs(np.cross(vec1, vec2)) / (np.linalg.norm([line_point1[0] - line_point2[0], line_point1[1] - line_point2[1]]) + 1e-12)
            if distance < threat_r:
                penalty_distance_set.append(distance/threat_r - 1)
    return penalty_distance_set


def calculate_threat(line_point1, line_point2, task_time, target_attack_time, targets, threat_r):
    survival_target = calculate_survival_target_points(task_time, target_attack_time, targets)
    penalty_distance = threat_function(line_point1, line_point2, survival_target, threat_r)
    return penalty_distance


def calculate_attack_task_order(uav_time_sequences, attack_target_sequences):
    target_attack_time = []
    for i in range(len(attack_target_sequences)):
        for j in range(len(attack_target_sequences[i])):
            target_attack_time.append([attack_target_sequences[i][j][0], uav_time_sequences[i][attack_target_sequences[i][j][1]]])
    return target_attack_time



