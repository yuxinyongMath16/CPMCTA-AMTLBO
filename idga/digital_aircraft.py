# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2022年09月21日
"""
import math

import matplotlib.pyplot as plt


def digital_point_transform(digital_point):
    point_x = []
    point_y = []
    for point in digital_point:
        point_x.append(point[0])
        point_y.append(point[1])
    return [point_x, point_y]


def image_rotate(image, angle, position):
    rotate_image = []
    for coordinate in image:
        x = (coordinate[0] - position[0])*math.cos(angle) - (coordinate[1] - position[1])*math.sin(angle) + position[0]
        y = (coordinate[0] - position[0])*math.sin(angle) + (coordinate[1] - position[1])*math.cos(angle) + position[1]
        rotate_image.append([x, y])
    return rotate_image


def image_resize(image, multiple, position):
    resize_image = []
    for coordinate in image:
        x = (coordinate[0] - position[0])*multiple + position[0]
        y = (coordinate[1] - position[1])*multiple + position[1]
        resize_image.append([x, y])
    return resize_image


def graphic_transformation(image, multiple, angle, position):
    if multiple != 1:
        image = image_resize(image, multiple, position)
    if angle != 0:
        image = image_rotate(image, angle, position)
    return image


def digital_transporter(position, multiple=1, angle=0):
    x = position[0]
    y = position[1]
    digital_point = [[x, y+1.9], [x+0.16, y+1.7], [x+0.28, y+1.4], [x+0.3, y], [x+1, y], [x+2.9, y-0.2], [x+2.88, y-0.5],
                     [x+0.3, y-0.8], [x+0.15, y-2.6], [x+1, y-2.9], [x+1, y-3.1], [x-1, y-3.1], [x-1, y-2.9],
                     [x-0.15, y-2.6], [x-0.3, y-0.8], [x-2.88, y-0.5], [x-2.9, y-0.2], [x-1, y],
                     [x-0.3, y], [x-0.28, y+1.4], [x-0.16, y+1.7], [x, y+1.9]]
    digital_point = graphic_transformation(digital_point, multiple, angle, position)
    transporter_list = digital_point_transform(digital_point)
    return transporter_list


def digital_airport(position, multiple=1, angle=0):
    x = position[0]
    y = position[1]
    digital_point = [[x+2, y+2], [x-2, y+2], [x-2, y-2], [x+2, y-2], [x+2, y+2]]
    digital_point = graphic_transformation(digital_point, multiple, angle, position)
    transporter_list = digital_point_transform(digital_point)
    return transporter_list


def digital_aircraft_carrier(position, multiple=1, angle=0):
    x = position[0]
    y = position[1]
    digital_point = [[x+3, y+1.5], [x+3.15, y+1], [x+6.2, y+0.5], [x+6.2, y-0.5], [x+3.15, y-1.1], [x+3, y-1.5],
                     [x-3.6, y-1.5], [x-4.6, y-0.8], [x-4.9, y+0.1], [x-4.4, y+1], [x-3.6, y+1.3], [x-2.7, y+1.3],
                     [x-2.7, y+1.3], [x-2.55, y+1.5], [x+3, y+1.5]]
    digital_point = graphic_transformation(digital_point, multiple, angle, position)
    carrier_list = digital_point_transform(digital_point)
    return carrier_list


def digital_target_ship(position, multiple=1, angle=0):
    x = position[0]
    y = position[1]
    digital_point = [[x-3, y+0.5], [x+1, y+0.5], [x+2, y+0.4], [x+2.4, y+0.3], [x+2.7, y+0.15], [x+3, y],
                     [x+2.7, y-0.15], [x+2.4, y-0.3], [x+2, y-0.4], [x+1, y-0.5], [x-3, y-0.5], [x-3, y+0.5]]
    digital_point = graphic_transformation(digital_point, multiple, angle, position)
    ship_list = digital_point_transform(digital_point)
    return ship_list


def digital_reconnaissance_uav(position, multiple=1, angle=0):
    x = position[0]
    y = position[1]
    digital_point = [[x, y+1.4], [x+0.1, y+1.37], [x+0.15, y+1.32], [x+0.2, y+1.28], [x+0.25, y+1.2], [x+0.1, y+0.1],
                     [x+0.15, y], [x+3.5, y-0.2], [x+3.5, y-0.4], [x+0.3, y-0.55], [x+0.15, y-0.65], [x+0.15, y-2],
                     [x+0.8, y-2.2], [x+0.8, y-2.4], [x, y-2.25], [x-0.8, y-2.4], [x-0.8, y-2.2], [x-0.15, y-2],
                     [x-0.15, y-0.65], [x-0.3, y-0.55], [x-3.5, y-0.4], [x-3.5, y-0.2], [x-0.15, y],
                     [x-0.1, y+0.1], [x-0.25, y+1.2], [x-0.2, y+1.28], [x-0.15, y+1.32], [x-0.1, y+1.37], [x, y+1.4]]
    digital_point = graphic_transformation(digital_point, multiple, angle, position)
    reconnaissance_list = digital_point_transform(digital_point)
    return reconnaissance_list


def digital_combat_uav(position, multiple=1, angle=0):
    x = position[0]
    y = position[1]
    # digital_point = [[x, y+3], [x+0.2, y+2.4], [x+0.35, y+1.2], [x+1.2, y+0.5], [x+1.2, y+0.3], [x+0.65, y+0.35],
    #                  [x+1.9, y-2.2], [x+0.6, y-2.5], [x+1.2, y-3.1], [x+0.4, y-3], [x+0.4, y-2.5], [x-0.4, y-2.5],
    #                  [x-0.4, y-3], [x-1.2, y-3.1], [x-0.6, y-2.5], [x-1.9, y-2.2], [x-0.65, y+0.35], [x-1.2, y+0.3],
    #                  [x-1.2, y+0.5], [x-0.35, y+1.2], [x-0.2, y+2.4], [x, y+3]]
    digital_point = [[x, y + 3], [x + 0.2, y + 2.4], [x + 0.35, y + 1.2], [x + 1.2, y + 0.5], [x + 1.2, y + 0.3],
                     [x + 0.65, y + 0.35], [x + 1.9, y - 2.2], [x + 0.6, y - 2.5], [x - 0.6, y - 2.5],
                     [x - 1.9, y - 2.2], [x - 0.65, y + 0.35], [x - 1.2, y + 0.3], [x - 1.2, y + 0.5],
                     [x - 0.35, y + 1.2], [x - 0.2, y + 2.4], [x, y + 3]]
    digital_point = graphic_transformation(digital_point, multiple, angle, position)
    combat_list = digital_point_transform(digital_point)
    return combat_list


def digital_ammunition_uav(position, multiple=1, angle=0):
    x = position[0]
    y = position[1]
    digital_point = [[x, y+2], [x+0.15, y+1.6], [x+0.15, y+0.8], [x+3.9, y-1.8], [x+3.9, y-2.2], [x+0.15, y-0.4],
                     [x+0.2, y-1.3], [x+0.1, y-2.55], [x+1.1, y-3.4], [x+1.1, y-3.7], [x, y-3.55], [x-1.1, y-3.7],
                     [x-1.1, y-3.4], [x-0.1, y-2.55], [x-0.2, y-1.3], [x-0.15, y-0.4], [x-3.9, y-2.2], [x-3.9, y-1.8],
                     [x-0.15, y+0.8], [x-0.15, y+1.6], [x, y+2]]
    digital_point = graphic_transformation(digital_point, multiple, angle, position)
    ammunition_list = digital_point_transform(digital_point)
    return ammunition_list


def plot_digital_aircraft(digital_list):
    plt.fill(digital_list[0], digital_list[1], color='cornflowerblue')
    plt.plot(digital_list[0], digital_list[1], 'k')
    plt.show()


def multi_digital_vehicle(vehicle_list):
    for vehicle in vehicle_list:
        if vehicle[0] == 0:
            vehicle_position = digital_transporter(vehicle[1], vehicle[2], vehicle[3])
        elif vehicle[0] == 1:
            vehicle_position = digital_aircraft_carrier(vehicle[1], vehicle[2], vehicle[3])
        elif vehicle[0] == 2:
            vehicle_position = digital_target_ship(vehicle[1], vehicle[2], vehicle[3])
        elif vehicle[0] == 3:
            vehicle_position = digital_reconnaissance_uav(vehicle[1], vehicle[2], vehicle[3])
        elif vehicle[0] == 4:
            vehicle_position = digital_combat_uav(vehicle[1], vehicle[2], vehicle[3])
        elif vehicle[0] == 5:
            vehicle_position = digital_ammunition_uav(vehicle[1], vehicle[2], vehicle[3])
        plt.fill(vehicle_position[0], vehicle_position[1], color='cornflowerblue')
        plt.plot(vehicle_position[0], vehicle_position[1], 'k')
    plt.show()


if __name__ == '__main__':
    position = [0, 0]
    # draw_list = digital_transporter(position)
    # draw_list = digital_aircraft_carrier(position)
    # draw_list = digital_target_ship(position)
    # draw_list = digital_reconnaissance_uav(position)
    # draw_list = digital_combat_uav(position)
    # draw_list = digital_ammunition_uav(position)
    # plot_digital_aircraft(draw_list)
    vehicle = [[0, [0, 0], 3, 0], [0, [0, 0], 3, math.pi/4], [1, [10, 10], 2, 0], [1, [10, 10], 2, math.pi/4],
               [2, [10, -10], 2, math.pi/2], [2, [10, -10], 2, 0], [3, [-10, 10], 2, 3*math.pi/4],
               [3, [-10, 10], 1, 0], [4, [-10, -10], 1, math.pi], [4, [-10, -10], 1, 0], [5, [-10, -15], 1, 0],
               [5, [-10, -15], 2, 3*math.pi/2]]
    # vehicle = [[0, [0, 0], 3, 0], [0, [0, 0], 3, math.pi/4], [3, [-10, 10], 2, 0], [3, [-10, 10], 1, 3*math.pi/4]]
    multi_digital_vehicle(vehicle)
