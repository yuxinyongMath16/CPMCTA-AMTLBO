 # Previous Version
def __intersect_pre(point_aa, point_bb,
                point_cc, point_dd):
    # this fuction will judge whether two line-segment is intersect
    # from https://stackoverflow.com/questions/563198/how-do-you-detect-where-two-line-segments-intersect
    s10_x = point_bb[0] - point_aa[0]
    s10_y = point_bb[1] - point_aa[1]
    s32_x = point_dd[0] - point_cc[0]
    s32_y = point_dd[1] - point_cc[1]

    denom = s10_x * s32_y - s32_x * s10_y
    if denom == 0:
        return False

    denomPositive = denom > 0

    s02_x = point_aa[0] - point_cc[0]
    s02_y = point_aa[1] - point_cc[1]
    s_numer = s10_x * s02_y - s10_y * s02_x
    if (s_numer < 0) == denomPositive:
        return False
    t_numer = s32_x * s02_y - s32_y * s02_x
    if (t_numer < 0) == denomPositive:
        return False

    if ((s_numer > denom) == denomPositive) or ((t_numer > denom) == denomPositive):
        return False

    return True


# New Version by Joshua Wen
def __intersect(point_aa, point_bb,
                point_cc, point_dd):
    # this fuction will judge whether two line-segment is intersect
    # from https://github.com/JoshuaWenHIT/Two-Line-Segment-Intersect
    # s10, 向量r
    s10_x = point_bb[0] - point_aa[0]
    s10_y = point_bb[1] - point_aa[1]
    # s32, 向量s
    s32_x = point_dd[0] - point_cc[0]
    s32_y = point_dd[1] - point_cc[1]
    # s20, 向量(q-p)
    s20_x = point_cc[0] - point_aa[0]
    s20_y = point_cc[1] - point_aa[1]

    # r x s
    denom = s10_x * s32_y - s32_x * s10_y
    denomPositive = denom > 0

    # 情况1和情况2
    if denom == 0:
        if (s20_x * s10_y - s20_y * s10_x) == 0:
            _mole_a = s20_x * s32_x + s20_y * s32_y
            # 参数m，介于[0,1]之间相交，此处乘了分母，范围扩展为[0,s^2]
            if _mole_a < 0:
                return False
            _mole_b = s20_x * s10_x + s20_y * s10_y
            # 参数n，介于[0,1],之间相交，此处乘了分母，范围扩展为[0,s^2],与m是或的关系
            if _mole_b < 0:
                return False
            print('打印出来看看问题', s32_x, s32_y)
            _denom = s32_x ** 2 + s32_y ** 2
            if _mole_a > _denom:
                return False
            if _mole_b > _denom:
                return False
            return True
        else:
            return False

    # 情况3 ,mole_a = (q-p) x r
    mole_a = s20_x * s10_y - s20_y * s10_x
    # ((q-p) x r <= 0) == r x s
    if (mole_a <= 0) == denomPositive:
        return False

    # mole_b = (q-p) x s
    mole_b = s20_x * s32_y - s20_y * s32_x
    if (mole_b <= 0) == denomPositive:
        return False

    if mole_a == denom and ((mole_b <= denom) == denomPositive):
        return True
    if mole_b == denom and ((mole_a <= denom) == denomPositive):
        return True
    if ((mole_a > denom) == denomPositive) or ((mole_b > denom) == denomPositive):
        return False

    return True


if __name__ == '__main__':
    '''
    测试结果：
    共线相交的情况判断不出来,,,多变形共线时，其他边与其交于一点，也能判断是有交点的
    鉴于我们的使用环境，此问题影响不大
    '''
    # point1, point2, point3, point4 = [1, 1], [2, 2], [1.5, 1], [2.5, 1]    # 不相交
    # point1, point2, point3, point4 = [1, 1], [2, 2], [1.3, 1.4], [2.5, 1.4]  # 相交
    # point1, point2, point3, point4 = [1, 1], [1, 2], [1.3, 1.4], [2.5, 1.4]  # 不相交（一条直线斜率不存在，一条直线斜率为0）
    # point1, point2, point3, point4 = [1, 1], [1, 2], [0.8, 1.4], [2.5, 1.4]  # 相交（一条直线斜率不存在，一条直线斜率为0）
    # point1, point2, point3, point4 = [1, 1], [1, 2], [1, -0.8], [1, 0.8]  # 不相交（两条直线共线，且斜率不存在）
    # 下面的例子有问题（判断错误），共线，无法判断出相交
    # point1, point2, point3, point4 = [1, 1], [1, 2], [1, -0.8], [1, 1.2]  # 相交（两条直线共线，且斜率不存在）

    # point1, point2, point3, point4 = [1, 1], [2, 2], [3, 3], [4, 4]  # 不相交（两条直线共线，且斜率存在）
    # 下面的例子有问题（会报错）平方符号使用错误，已更正
    # point1, point2, point3, point4 = [1, 1], [2, 2], [1.5, 1.5], [4, 4]  # 相交（两条直线共线，且斜率存在）

    # point1, point2, point3, point4 = [1, 1], [3, 1], [3.2, 1], [4.2, 1]  # 不相交（两条直线共线，且斜率为0）
    # 下面的例子有问题（判断错误），共线，无法判断出相交
    point1, point2, point3, point4 = [1, 1], [3, 1], [0.8, 1], [4.2, 1]  # 相交（两条直线共线，且斜率为0）

    # point1, point2, point3, point4 = [1, 1], [3, 1], [1, 2], [4.2, 2]  # 不相交（两条直线平行，且斜率为0）
    # point1, point2, point3, point4 = [1, 3], [1, 4], [4.2, 2], [4.2, 3.8]  # 不相交（两条直线平行，且斜率不存在）
    # point1, point2, point3, point4 = [-1, 1], [-3, 3], [-1, 2], [-3, 4]  # 不相交（两条直线平行，且斜率存在）
    # point1, point2, point3, point4 = [-1, 1], [-3, 3], [-1, 2], [-3, 3.8]  # 不相交（两条直线平行，且斜率存在）
    res = __intersect(point1, point2, point3, point4)
    print('结果是:', res)