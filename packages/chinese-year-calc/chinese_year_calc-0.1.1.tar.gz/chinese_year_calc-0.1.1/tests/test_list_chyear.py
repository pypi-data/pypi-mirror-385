from chyear import *

year = 2021

# 测试列表
tiangan = get_chinese_year(year, TIANGAN)
dizhi = get_chinese_year(year, DIZHI)
shengxiao = get_chinese_year(year, SHENGXIAO)
dizhi2 = get_chinese_year(year, DIZHI | TIANGAN)
zhigan = get_chinese_year(year, ZHIGAN)
dizhi_shengxiao = get_chinese_year(year, DIZHI_SHENGXIAO)
info = get_chinese_year(year, ALL)
all_add_year_end = get_chinese_year(year, ALL | ADD_YEAR_END)
try:
    all_add_year_end_err = get_chinese_year(year, ADD_YEAR_END)
except Exception as e:
    print('错误：', e)

# 测试列表输出
print(TIANGAN_LIST) # 输出：['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
print(DIZHI_LIST) # 输出：['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
print(SHENGXIAO_LIST) # 输出：['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
print(tiangan)
print(dizhi)
print(shengxiao)
print(dizhi2)
print(zhigan)
print(dizhi_shengxiao)
print(info)
print(all_add_year_end)
