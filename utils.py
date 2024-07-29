from enum import Enum
import re

class Operator(Enum):
    MOKA = 1
    MICHIRU = 2
    WOODY = 3
    DAMAGE = 4
    TRIGGER = 5
    
    def __str__(self):
        if self == Operator.MOKA:
            return "Moka"
        elif self == Operator.MICHIRU:
            return "Michiru"
        elif self == Operator.WOODY:
            return "Woody"
        elif self == Operator.DAMAGE:
            return "Damage"
        elif self == Operator.TRIGGER:
            return "Trigger"
        else:
            raise ValueError(f"Invalid operator: {self}")
        
def parse_operator(operator):
        """解析操作符，调用对应的函数"""
        operator = operator.lower()  # 转换为小写以处理大小写不敏感的问题
        moka_match = re.match(r'moka\((\d+)\)', operator)
        michiru_match = re.match(r'michiru\((\d+)\)', operator)
        woody_match = re.match(r'woody\((\d+)\)', operator)
        damage_trigger_match = re.match(r'(\d+)t', operator)
        damage_match = re.match(r'(\d+)', operator)
        
        if moka_match:
            num = int(moka_match.group(1))
            return (Operator.MOKA, num)
        elif michiru_match:
            num = int(michiru_match.group(1))
            return (Operator.MICHIRU, num)
        elif woody_match:
            num = int(woody_match.group(1))
            return (Operator.WOODY, num)
        elif damage_trigger_match:
            damage = int(damage_trigger_match.group(1))
            return (Operator.TRIGGER, damage)
        elif damage_match:
            damage = int(damage_match.group(1))
            return (Operator.DAMAGE, damage)
        else:
            raise ValueError(f"Invalid operator: {operator}")

def to_str(operator):
    if operator[0] == Operator.MOKA:
        return f"Moka({operator[1]})"
    elif operator[0] == Operator.MICHIRU:
        return f"Michiru({operator[1]})"
    elif operator[0] == Operator.WOODY:
        return f"Woody({operator[1]})"
    elif operator[0] == Operator.DAMAGE:
        return f"{operator[1]}"
    elif operator[0] == Operator.TRIGGER:
        return f"{operator[1]}T"
    else:
        raise ValueError(f"Invalid operator: {operator}")

def to_str_group(operator_group):
    '''
    Convert the operator group to a string
    '''
    return '+'.join([to_str(op) for op in operator_group])

def parse_operator_group(operator_group):
    '''
    Parse the operator group from a string
    '''
    operator_group_ = operator_group.split('+')
    operator_list = []
    for op in operator_group_:
        operator, times = parse_operator(op)
        operator_list.append((operator, times))
    return tuple(operator_list)

def find_max_repeated_sublist(lst):
    n = len(lst)
    # 找出n的所有因子
    max_count = 1
    max_sublist = lst
    for i in range(1, n + 1):
        if n % i == 0:
            count = n // i
            sublist = lst[:i]
            found = True
            for j in range(1, n // i):
                if lst[j * i: (j + 1) * i] != sublist:
                    found = False
                    break
            # 找到了重复的子列表
            if found and count > max_count:
                max_count = count
                max_sublist = sublist
    
    return max_sublist, max_count

def to_str_list(operator_list):
    # Check if the operator list is a repetition of the same combination of operators
    max_sublist, max_count = find_max_repeated_sublist(operator_list)
    if max_count > 1:
        return '[' + ', '.join([to_str(op) for op in max_sublist]) + f'] * {max_count}'
    else:
        return '[' + ', '.join([to_str(op) for op in operator_list]) + ']'
    