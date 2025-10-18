import argparse
import chyear

def parse_args_to_style_num(items):
    mapping = {'TIANGAN':0b1, 'DIZHI':0b10, 'SHENGXIAO':0b100, 'ZHIGAN': 0b11, 'TIANGAN_SHENGXIAO': 0b110, 'ALL': 0b111, 'ADD_YEAR_END': 0b1000} # 定义映射
    try:
        return sum(mapping[item.upper()] for item in set(items)) # 计算并返回结果
    except KeyError as e:
        raise ValueError(f"未定义的项: '{e.args[0]}'") # 未定义的项错误

def main():
    parser = argparse.ArgumentParser(description='中国年份计算器') # 创建主命令

    parser.add_argument('year', type=int, help='想要计算的年份') # 创建年份参数
    parser.add_argument('info', type=str, help='想要查询的中国年份信息', nargs='+')
    parser.add_argument('--add-year-end', '-y', action='store_true', help='是否增加"年"字到结尾')
    
    args = parser.parse_args() # 解析参数
    
    try:
        style_num = parse_args_to_style_num(args.info + (['ADD_YEAR_END'] if args.add_year_end else [])) # 解析样式参数
    except ValueError as e:
        print(f'解析计算信息参数错误:{e}')
        exit(1) # 错误退出
    print(chyear.get_chinese_year(args.year, style_num))

if __name__ == '__main__':
    main()