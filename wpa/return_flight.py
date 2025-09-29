# -*- coding:utf-8 -*-

"""
作者：yuxinyong
日期：2022年09月15日
返航路径计算
"""
import math

def calculate_distance(point1, point2):
    distance = math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
    return distance

def current_airport_location_angle(point1, point2):
    if point1[0] - point2[0] == 0:
        # print('无斜率')
        if point2[1] - point1[1] >= 0:
            direction = math.pi / 2
        else:
            direction = math.pi * 3 / 2
    else:
        k = (point1[1] - point2[1]) / (point1[0] - point2[0])
        # print('斜率是：', k)
        if point2[0] - point1[0] < 0:
            direction = math.pi + math.atan(k)
        else:
            if math.atan(k) > 0:
                direction = math.atan(k)
                # print('反正切函数是：', math.atan(k))
            else:
                direction = math.pi * 2 + math.atan(k)
    return direction


# 返回最终回到机场时，机场的坐标，输入[机场类，uav类，uav最后的一点，之前的航程]
def return_airport_point(airport, uav, point, voyage_time):
    time1 = voyage_time
    point1 = airport.next_position_calculate(time1)
    x = calculate_distance(point1, point)
    time2 = x/uav.speed
    final_airport_position = airport.next_position_calculate(time1 + time2)
    # airport.airport_track_update([final_airport_position, time1 + time2])
    return final_airport_position, time1+time2


# 返回最终回到机场时，机场的坐标，输入[机场类，uav类，uav最后的一点，之前的航程]
def return_airport_point1(airport, uav, point, voyage):
    time1 = voyage/uav.speed
    point1 = airport.next_position_calculate(time1)
    point2 = point
    print('点一和点二分别是', point1, point2)
    alpha = current_airport_location_angle(point1, point2)
    beta = airport.direction
    if alpha > beta:
        delta = alpha - beta
    else:
        delta = beta - alpha
    x = calculate_distance(point1, point2)
    a = airport.speed**2 - uav.speed**2
    b = -2*x*airport.speed*math.cos(delta)
    c = x**2
    print(a, b, c, x, delta)
    time2 = min(abs((-b - math.sqrt(b**2-4*a*c)) / 2*a), abs((-b + math.sqrt(b**2-4*a*c)) / 2*a))
    print('打印一些信息', time2)
    final_airport_position = airport.next_position_calculate(time1+time2)
    print(final_airport_position)
    airport.airport_track_update([final_airport_position, time1+time2])
    return final_airport_position


if __name__ == '__main__':
    point1 = [0, 0]
    point2 = [-1, 1]  # 3/4
    point3 = [1, 1]   # 1/4
    point4 = [-1, -1]  # 5/4
    point5 = [1, -1]   # 7/4
    point6 = [0, 1]    # 1/2
    point7 = [0, -1]   # 3/2
    print(current_airport_location_angle(point1, point7) / 3.1415926535)