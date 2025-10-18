# 定义计算信息量
TIANGAN = 0b1
DIZHI = 0b10
SHENGXIAO = 0b100
ZHIGAN = TIANGAN | DIZHI
DIZHI_SHENGXIAO = DIZHI | SHENGXIAO
ALL = TIANGAN | DIZHI | SHENGXIAO
ADD_YEAR_END = 0b1000

# 定义常见的表格
TIANGAN_LIST = ['甲','乙','丙','丁','戊','己','庚','辛','壬','癸']
DIZHI_LIST = ['子','丑','寅','卯','辰','巳','午','未','申','酉','戌','亥']
SHENGXIAO_LIST = ['鼠','牛','虎','兔','龙','蛇','马','羊','猴','鸡','狗','猪']

def get_chinese_year(year: int, infos: int):
    '''
    将公元年份转换为中国化的年份(如天干地支)

    :example:
    >>> get_chinese_year(2021, ALL | ADD_YEAR_END) # 获取2021年的所有信息，并在最后加上'年'
    '辛丑牛年'

    :param year: int, 要计算的年份
    :param infos: int, 信息类型，TIANGAN表示天干，DIZHI表示地支，SHENGXIAO表示生肖。还可以组合使用，TIANGAN | DIZHI 表示同时输出天干地支。等同于GANZHI，SHENGXIAO | DIZHI = 同时输出生肖地支，等同于DIZHI_SHENGXIAO。TIANGAN | DIZHI | SHENGXIAO 表示同时输出所有信息，等同于ALL。ADD_YEAR_END表示在字符最后加上'年'

    :return: str, 返回指定信息的中文化年份。
    
    :raises TypeError: 没有在ADD_YEAR_END中指定要获取的信息。
    '''
    if infos == ADD_YEAR_END:
        raise TypeError("未指定信息。")
    
    output = ''

    # 计算方式：公元4年为甲子年基准，每60年一轮
    offset = (year - 4) % 60 # 计算偏移量
    tiangan_index = offset % 10 # 计算天干索引
    dizhi_index = offset % 12 # 计算地支索引
    if infos & TIANGAN:
        output += TIANGAN_LIST[tiangan_index]
    if infos & DIZHI:
        output += DIZHI_LIST[dizhi_index]
    if infos & SHENGXIAO:
        output += SHENGXIAO_LIST[dizhi_index]
    if infos & ADD_YEAR_END:
        output += '年'

    return output
