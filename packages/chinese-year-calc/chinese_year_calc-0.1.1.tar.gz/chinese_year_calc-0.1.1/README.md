# chinese-year-calc
中国纪年计算器。

## 用法
### 主用法
使用`TIANGAN`获取年份的天干
```python
from chyear import (get_chinese_year, TIANGAN)

year = 2021
tiangan = get_chinese_year(year, TIANGAN)
print(tiangan) # 输出：'辛'
```
使用`DIZHI`获取年份的地支
```python
from chyear import (get_chinese_year, DIZHI)

year = 2021
dizhi = get_chinese_year(year, DIZHI)
print(dizhi) # 输出：'丑'
```

使用`SHENGXIAO`获取年份的生肖
```python
from chyear import (get_chinese_year, SHENGXIAO)

year = 2021
shengxiao = get_chinese_year(year, SHENGXIAO)
print(shengxiao) # 输出：'牛'
```

可以使用位运算符号`|`来组合信息
```python
from chyear import (get_chinese_year, DIZHI, TIANGAN)

year = 2021
dizhi_tiangan = get_chinese_year(year, DIZHI | TIANGAN)
print(dizhi) # 输出：'辛丑'
```

`DIZHI | TIANGAN`等价于`ZHIGAN`
```python
from chyear import (get_chinese_year, ZHIGAN)

year = 2021
zhigan = get_chinese_year(year, ZHIGAN)
print(dizhi) # 输出：'辛丑'
```

`DIZHI | SHENGXIAO`等价于`DIZHI_SHENGXIAO`
```python
from chyear import (get_chinese_year, DIZHI_SHENGXIAO)

year = 2021
dizhi_shengxiao = get_chinese_year(year, DIZHI_SHENGXIAO)
print(dizhi) # 输出：'丑牛'
```
`ALL`可以获取全部信息, 即`TIANGAN | DIZHI | SHENGXIAO`
```python
from chyear import (get_chinese_year, ALL)

year = 2021
info = get_chinese_year(year, ALL)
print(info) # 输出：'辛丑牛'
```

`ADD_YEAR_END`可以在字符最后加上'年'
> [!NOTE]
> `ADD_YEAR_END`参数不能单独使用，必须和其他年份计算一起使用，否则会报错`TypeError:未指定信息。`。
```python
from chyear import (get_chinese_year, ADD_YEAR_END, ALL)

year = 2021
all_add_year_end = get_chinese_year(year, ALL | ADD_YEAR_END)
print(info) # 输出：'辛丑牛年'
```

### 其他变量
TIANGAN_LIST获取天干列表。
DIZHI_LIST获取地支列表。
SHENGXIAO_LIST获取生肖列表。
```python
from chyear import (TIANGAN_LIST, DIZHI_LIST, SHENGXIAO_LIST)

print(TIANGAN_LIST) # 输出：['甲', '乙', '丙', '丁', '戊', '己', '庚', '辛', '壬', '癸']
print(DIZHI_LIST) # 输出：['子', '丑', '寅', '卯', '辰', '巳', '午', '未', '申', '酉', '戌', '亥']
print(SHENGXIAO_LIST) # 输出：['鼠', '牛', '虎', '兔', '龙', '蛇', '马', '羊', '猴', '鸡', '狗', '猪']
```

## 命令行

命令行用法

```bash
chyear year calc_info [calc_info1 [calc_info2 [...]]] [--add-year-end | -y]
```
calc_info可以是`TIANGAN`, `DIZHI`, `SHENGXIAO`, `ALL`, `ZHIGAN`和`SHENGXIAO_TIANGAN`中的一个或多个, 语法跟python的用法一样。
如：
```bash
chyear 2021 TIANGAN DIZHI SHENGXIAO --add-year-end # 相当于get_chinese_year(2021, TIANGAN | DIZHI | SHENGXIAO | ADD_YEAR_END), 输出：'辛丑牛年'
```