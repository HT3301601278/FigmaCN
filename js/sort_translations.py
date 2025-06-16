#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys

def read_file_lines(file_path):
    """读取文件所有行"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def extract_translation_pairs(lines):
    """从文件行中提取翻译键值对"""
    pairs = []
    array_started = False
    
    for line in lines:
        line = line.strip()
        
        # 检查数组开始
        if line.startswith('const allData = ['):
            array_started = True
            continue
            
        # 检查数组结束
        if array_started and line == ']':
            break
            
        # 提取数组内的键值对
        if array_started and line.startswith('[`') and '`],' in line:
            # 从行中提取键值对
            # 找到第一个逗号的位置，用于分隔键和值
            match = re.match(r'\[\s*(`.*?`)\s*,\s*(`.*?`)\s*\],?', line)
            if match:
                key, value = match.groups()
                pairs.append((key, value))
    
    return pairs

def custom_sort_key(pair):
    """自定义排序键函数，优化时间相关项的排序"""
    key = pair[0].strip('` ')
    
    # 识别时间格式的模式，如 "1 hour ago", "2 days ago", "3 months ago"
    time_pattern = re.match(r'^(\d+)\s+(hour|day|month|year)s?\s+ago$', key)
    if time_pattern:
        num, unit = time_pattern.groups()
        # 为时间单位定义优先级顺序
        unit_priority = {'hour': 1, 'day': 2, 'month': 3, 'year': 4}
        # 返回 (单位优先级, 数字) 作为排序键
        return (unit_priority.get(unit, 999), int(num))
    
    # 非时间相关项按字母排序
    return (999, 0, key.lower())

def sort_pairs(pairs):
    """排序键值对，时间相关项优先处理"""
    # 提取所有与时间相关的条目
    time_entries = []
    other_entries = []
    
    for pair in pairs:
        key = pair[0].strip('` ')
        if re.match(r'^\d+\s+(hour|day|month|year)s?\s+ago$', key):
            time_entries.append(pair)
        else:
            other_entries.append(pair)
    
    # 对时间相关条目使用自定义排序
    sorted_time_entries = sorted(time_entries, key=custom_sort_key)
    # 其他条目按字母顺序排序
    sorted_other_entries = sorted(other_entries, key=lambda x: x[0].strip('` ').lower())
    
    # 返回合并的列表，先放时间条目，然后是其他条目
    return sorted_time_entries + sorted_other_entries

def write_sorted_file(file_path, original_lines, sorted_pairs):
    """写入排序后的文件"""
    with open(file_path, 'w', encoding='utf-8') as f:
        # 写入文件头部
        f.write('const allData = [\n')
        
        # 写入排序后的键值对
        for key, value in sorted_pairs:
            f.write(f'  [{key}, {value}],\n')
        
        # 找到原始文件中数组结束的位置
        array_started = False
        array_ended = False
        
        for line in original_lines:
            # 检查数组开始
            if 'const allData = [' in line:
                array_started = True
                continue
                
            # 检查是否已经到了数组结束部分
            if array_started and not array_ended:
                stripped_line = line.strip()
                if stripped_line == ']' or stripped_line == '];':
                    f.write(']\n\n')  # 写入数组结束符号并保留空行
                    array_ended = True
                continue
                
            # 数组结束后，保留所有后续代码
            if array_ended:
                f.write(line)

def main():
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置输入和输出文件的完整路径
    input_file = os.path.join(script_dir, 'content.js')
    output_file = os.path.join(script_dir, 'content_sorted.js')
    
    # 支持命令行参数指定输入文件
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        # 如果指定了输入文件，则在同一目录下生成输出文件
        output_dir = os.path.dirname(input_file)
        output_file = os.path.join(output_dir, 'content_sorted.js')
    
    if not os.path.exists(input_file):
        print(f"错误：找不到文件 {input_file}")
        return
    
    # 读取文件所有行
    lines = read_file_lines(input_file)
    
    # 提取翻译键值对
    pairs = extract_translation_pairs(lines)
    
    if not pairs:
        print("警告：未找到任何翻译键值对！")
        print("请检查文件格式是否符合预期。")
        return
    
    # 排序键值对
    sorted_pairs = sort_pairs(pairs)
    
    # 写入排序后的文件
    write_sorted_file(output_file, lines, sorted_pairs)
    
    print(f"排序完成！排序后的内容已保存到 {output_file}")
    print(f"共处理了 {len(pairs)} 对翻译")

if __name__ == "__main__":
    main() 