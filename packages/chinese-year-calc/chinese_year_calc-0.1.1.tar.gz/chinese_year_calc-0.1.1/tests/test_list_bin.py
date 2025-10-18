
def binary_or(items):
    mapping = {'a':0b1, 'b':0b10, 'c':0b100}
    try:
        return sum(mapping[item] for item in set(items))
    except KeyError as e:
        raise ValueError(f"未定义的项: '{e.args[0]}'")

if __name__ == "__main__":
    print(binary_or(['a', 'b', 'b', 'c']))  # 输出: 3
