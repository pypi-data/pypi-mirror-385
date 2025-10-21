#!/usr/bin/env python3
"""
反馈导出模块
从Excel文件中导出AI演示组件的对话详情
"""

import os
import sys
import pandas as pd
from typing import Optional, List, Tuple
import glob
import re


def read_excel_file(file_path: str, sheet_name: Optional[str] = None) -> Optional[pd.DataFrame]:
    """读取Excel文件的指定sheet表或最新sheet表"""
    try:
        # 读取Excel文件的所有sheet
        excel_file = pd.ExcelFile(file_path)
        
        if len(excel_file.sheet_names) == 0:
            print(f"错误: Excel文件 {file_path} 中没有找到任何sheet表")
            return None
        
        # 如果指定了表名，使用指定的表名；否则使用最新的表（倒数第二个）
        if sheet_name:
            if sheet_name not in excel_file.sheet_names:
                print(f"错误: 指定的表名 '{sheet_name}' 不存在")
                print(f"可用的表名: {excel_file.sheet_names}")
                return None
            target_sheet = sheet_name
            print(f"正在读取指定的sheet表: {target_sheet}")
        else:
            target_sheet = excel_file.sheet_names[-2]
            print(f"正在读取最新的sheet表: {target_sheet}")
        
        # 读取指定的sheet表
        df = pd.read_excel(file_path, sheet_name=target_sheet)
        print(f"成功读取 {target_sheet} 表，共 {len(df)} 行数据")
        
        return df
        
    except FileNotFoundError:
        print(f"错误: 文件 {file_path} 不存在")
        return None
    except Exception as e:
        print(f"错误: 读取Excel文件失败: {e}")
        return None


def find_ai_demo_components(df: pd.DataFrame) -> List[Tuple[int, str]]:
    """查找满足条件的行，返回行号和对话详情"""
    results = []
    

    
    # 查找对话详情列（可能的不同列名）
    detail_columns = ['对话详情1', '对话详情', 'detail', 'Detail', 'DETAIL']
    detail_col = None
    
    for col in detail_columns:
        if col in df.columns:
            detail_col = col
            break
    
    if detail_col is None:
        print("错误: 未找到对话详情列，请检查Excel文件结构")
        print(f"可用的列名: {list(df.columns)}")
        return []
    
    # 查找业务归属列
    business_columns = ['业务归属', 'business', 'Business', 'BUSINESS']
    business_col = None
    
    for col in business_columns:
        if col in df.columns:
            business_col = col
            break
    
    if business_col is None:
        print("错误: 未找到业务归属列，请检查Excel文件结构")
        print(f"可用的列名: {list(df.columns)}")
        return []
    
    # 查找一级分类列
    category_columns = ['一级分类=AI组件', '一级分类', 'category', 'Category', 'CATEGORY']
    category_col = None
    
    for col in category_columns:
        if col in df.columns:
            category_col = col
            break
    
    if category_col is None:
        print("错误: 未找到一级分类列，请检查Excel文件结构")
        print(f"可用的列名: {list(df.columns)}")
        return []
    
    print(f"使用列: 对话详情列='{detail_col}', 业务归属列='{business_col}', 一级分类列='{category_col}'")
    
    # 遍历数据，查找满足条件的行
    for index, row in df.iterrows():
        business_value = str(row[business_col]).strip()
        category_value = str(row[category_col]).strip()
        
        # 检查条件：
        # 1. 业务归属为"AI"、"AI-会员"或"AI-365"
        # 2. 一级分类为"演示"
        if (business_value in ["AI", "AI-会员", "AI-365"] and 
            category_value == "演示"):
            
            detail_text = str(row[detail_col]).strip()
            if detail_text and detail_text != 'nan':
                # Excel行号从1开始，pandas索引从0开始，但Excel通常有表头行，所以+2
                excel_row_number = index + 2
                results.append((excel_row_number, detail_text))
                print(f"找到满足条件的行: 业务归属={business_value}, 一级分类={category_value}, 行号: {excel_row_number}")
    
    return results


def create_output_directory() -> str:
    """创建输出目录"""
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, "客服")
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"输出目录: {output_dir}")
        return output_dir
    except Exception as e:
        print(f"错误: 创建输出目录失败: {e}")
        return current_dir


def export_to_txt_files(output_dir: str, results: List[Tuple[int, str]]) -> bool:
    """将对话详情导出到txt文件"""
    if not results:
        print("没有找到需要导出的数据")
        return False
    
    success_count = 0
    
    for row_number, detail_text in results:
        # 文件名使用行号
        filename = f"{row_number}.txt"
        file_path = os.path.join(output_dir, filename)
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(detail_text)
            print(f"✓ 已导出: {filename}")
            success_count += 1
            
        except Exception as e:
            print(f"✗ 导出 {filename} 失败: {e}")
    
    print(f"\n导出完成: 成功 {success_count}/{len(results)} 个文件")
    return success_count > 0


def command_feedback_export(file_path: str, sheet_name: Optional[str] = None) -> None:
    """反馈导出命令主函数"""
    print("========================================")
    print("反馈导出工具")
    print("========================================")
    print()
    
    # 检查文件是否存在
    if not os.path.exists(file_path):
        print(f"错误: 文件 {file_path} 不存在")
        sys.exit(1)
    
    # 检查文件扩展名
    if not file_path.lower().endswith(('.xlsx', '.xls')):
        print(f"错误: 文件 {file_path} 不是有效的Excel文件")
        print("支持的文件格式: .xlsx, .xls")
        sys.exit(1)
    
    print(f"正在处理Excel文件: {file_path}")
    if sheet_name:
        print(f"指定表名: {sheet_name}")
    print()
    
    # 读取Excel文件
    df = read_excel_file(file_path, sheet_name)
    if df is None:
        sys.exit(1)
    
    # 查找满足条件的数据
    print("正在查找满足条件的数据...")
    print("筛选条件: 业务归属为'AI'、'AI-会员'或'AI-365' 且 一级分类为'演示'")
    results = find_ai_demo_components(df)
    
    if not results:
        print("未找到任何满足条件的数据")
        sys.exit(1)
    
    print(f"找到 {len(results)} 个满足条件的数据")
    print()
    
    # 创建输出目录
    output_dir = create_output_directory()
    
    # 导出到txt文件
    print("正在导出对话详情...")
    if export_to_txt_files(output_dir, results):
        print(f"\n所有文件已成功导出到: {output_dir}")
    else:
        print("\n导出过程中出现错误")
        sys.exit(1)


def format_txt_files(directory: str = None) -> bool:
    """格式化txt文件，在特定关键词前添加换行符"""
    if directory is None:
        directory = os.getcwd()
    
    # 查找所有txt文件
    txt_files = glob.glob(os.path.join(directory, "*.txt"))
    
    if not txt_files:
        print(f"在目录 {directory} 中未找到任何txt文件")
        return False
    
    print(f"找到 {len(txt_files)} 个txt文件")
    
    # 定义需要在前面添加换行符的关键词
    keywords = [
        "客服",
        "用户",
        "客户",
    ]
    
    success_count = 0
    
    for txt_file in txt_files:
        try:
            # 读取文件内容
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 为每个关键词添加换行符
            for keyword in keywords:
                # 使用字符串分割和连接的方法，性能更好
                parts = content.split(keyword)
                if len(parts) > 1:
                    content = f'\n{keyword}'.join(parts)
            
            # 处理连续的回车符，将两个以上连续的回车符替换为一个回车符
            while '\n\n\n' in content:
                content = content.replace('\n\n\n', '\n\n')
            
            # 如果内容有变化，写回文件
            if content != original_content:
                with open(txt_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"✓ 已格式化: {os.path.basename(txt_file)}")
                success_count += 1
            else:
                print(f"- 无需格式化: {os.path.basename(txt_file)}")
                
        except Exception as e:
            print(f"✗ 格式化 {os.path.basename(txt_file)} 失败: {e}")
    
    print(f"\n格式化完成: 成功处理 {success_count}/{len(txt_files)} 个文件")
    return success_count > 0


def command_feedback_format() -> None:
    """反馈格式化命令主函数"""
    print("========================================")
    print("客服原语格式化工具")
    print("========================================")
    print()
    
    current_dir = os.getcwd()
    print(f"正在处理目录: {current_dir}")
    print()
    
    # 格式化txt文件
    print("正在格式化txt文件...")
    if format_txt_files(current_dir):
        print(f"\n格式化完成！文件已保存在: {current_dir}")
    else:
        print("\n格式化过程中出现错误或没有文件需要处理")


if __name__ == "__main__":
    if len(sys.argv) < 2 or len(sys.argv) > 3:
        print("用法: python feedback_export.py <Excel文件路径> [表名]")
        print("示例: python feedback_export.py data.xlsx")
        print("示例: python feedback_export.py data.xlsx 'Sheet1'")
        sys.exit(1)
    
    file_path = sys.argv[1]
    sheet_name = sys.argv[2] if len(sys.argv) == 3 else None
    
    command_feedback_export(file_path, sheet_name) 