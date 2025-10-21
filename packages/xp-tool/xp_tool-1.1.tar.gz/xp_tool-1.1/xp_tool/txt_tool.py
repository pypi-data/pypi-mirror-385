import pandas as pd
import json

class TxtTool:
    """快捷处理本地txt文件"""
    
    def __init__(self,txt_path=None):
        self.txt_path = txt_path

    def write(self,content,way = 'w',encoding='utf-8'):
        allowed_values = ['w','a']
        if way not in allowed_values:
            raise ValueError("写入方式错误！目前只能为覆盖：'w'和追加：'a'嗷！")
        try:
            with open(self.txt_path,way,encoding=encoding) as file:
                file.write(content)
                print('Done！')
        except Exception as e:
            print(f'Oops!出错 {e}')

    def read(self,encoding='utf-8'):
        try:
            with open(self.txt_path, 'r', encoding=encoding) as file:
                content = file.read()
                return content
        except FileNotFoundError:
                print('文件搁哪儿呢？我没找到啊，看看文件路径有没有问题。')

    def json_read(self,json_path,encoding='utf-8'):
        try:
            with open(json_path, 'r', encoding=encoding) as file:
                data = json.load(file)
                print(data)
        except FileNotFoundError:
            print("文件搁哪儿呢？我没找到啊，看看文件路径有没有问题。")
        except json.JSONDecodeError:
            print("碰到无法解析的 JSON 数据了")
        except Exception as e:
            print(f"Oops!出错 {e}")

    def tell(self,encoding='utf-8'):
        try:
            with open(self.txt_path, 'r', encoding=encoding) as file:
                position = file.tell()
                print(f'当前指针位置: {position}')
        except FileNotFoundError:
            print('文件搁哪儿呢？我没找到啊，看看文件路径有没有问题。')
        except Exception as e:
            print(f'Oops!出错 {e}')

    def seek(self,seek,encoding='utf-8'):
        try:
            with open(self.txt_path, 'r+', encoding=encoding) as file:
                first_n_chars = file.read(seek)
                return first_n_chars
        except FileNotFoundError:
            print('文件搁哪儿呢？我没找到啊，看看文件路径有没有问题。')
        except Exception as e:
            print(f'Oops!出错 {e}')