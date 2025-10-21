import os
import io
import pandas as pd
import oss2
from oss2.exceptions import ClientError
from typing import Optional
from dotenv import load_dotenv

class OSSHandler:
    """处理本地文件与阿里云OSS的交互，并提供将OSS中的Excel转换为pandas DataFrame的功能"""
    
    def __init__(self, access_key_id: str = None, access_key_secret: str = None, endpoint: str = None, bucket_name: str = None):
        """
        初始化OSS连接
        
        :param access_key_id: 阿里云访问密钥ID
        :param access_key_secret: 阿里云访问密钥Secret
        :param endpoint: OSS服务的访问域名
        :param bucket_name: OSS存储桶名称
        """
        if not access_key_id:
            load_dotenv()
            access_key_id = os.getenv("ACCESS_KEY_ID")
            access_key_secret = os.getenv("ACCESS_KEY_SECRET")
            endpoint = os.getenv("ENDPOINT")
            bucket_name = os.getenv("BUCKET_NAME")
            
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        # 获取存储桶对象
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name)
        
    def upload_to_oss(self, local_file_path: str, oss_file_path: str) -> bool:
        """
        将本地文件上传到OSS
        
        :param local_file_path: 本地文件路径
        :param oss_file_path: OSS中保存的文件路径
        :return: 上传成功返回True，否则返回False
        """
        try:
            # 检查本地文件是否存在
            if not os.path.exists(local_file_path):
                print(f"错误: 本地文件 {local_file_path} 不存在")
                return False
                
            # 检查文件是否为Excel文件
            if not (local_file_path.endswith('.xlsx') or local_file_path.endswith('.xls')):
                print(f"错误: {local_file_path} 不是Excel文件")
                return False
                
            # 上传文件
            self.bucket.put_object_from_file(oss_file_path, local_file_path)
            print(f"文件 {local_file_path} 已成功上传至OSS: {oss_file_path}")
            return True
            
        except ClientError as e:
            print(f"OSS上传错误: {str(e)}")
            return False
        except Exception as e:
            print(f"上传文件时发生错误: {str(e)}")
            return False
    
    def get_excel_from_oss(self, oss_file_path: str) -> Optional[pd.DataFrame]:
        """
        从OSS获取Excel文件并转换为pandas DataFrame
        
        :param oss_file_path: OSS中的Excel文件路径
        :return: 转换后的DataFrame，如果出错则返回None
        """
        try:
            # 检查文件是否存在于OSS
            if not self.bucket.object_exists(oss_file_path):
                print(f"错误: OSS文件 {oss_file_path} 不存在")
                return None
                
            # 检查文件是否为Excel文件
            if not (oss_file_path.endswith('.xlsx') or oss_file_path.endswith('.xls')):
                print(f"错误: {oss_file_path} 不是Excel文件")
                return None
                
            # 从OSS下载文件到内存
            response = self.bucket.get_object(oss_file_path)
            excel_content = response.read()
            
            # 将内容转换为DataFrame
            # 使用BytesIO创建内存文件对象
            with io.BytesIO(excel_content) as excel_file:
                # 读取Excel文件，这里假设只有一个工作表
                df = pd.read_excel(excel_file)
                
            print(f"已成功从OSS获取文件 {oss_file_path} 并转换为DataFrame")
            return df
            
        except ClientError as e:
            print(f"OSS下载错误: {str(e)}")
            return None
        except Exception as e:
            print(f"获取并转换文件时发生错误: {str(e)}")
            return None
    def download_file(self, oss_file_path, local_file_path):
        """
        从OSS下载文件到本地
        
        :param oss_file_path: OSS上的文件路径
        :param local_file_path: 本地保存文件路径
        :return: 下载是否成功
        """
        try:
            # 检查文件是否存在
            if not self.bucket.object_exists(oss_file_path):
                print(f"OSS上不存在文件: {oss_file_path}")
                return False
            
            # 下载文件
            result = self.bucket.get_object_to_file(oss_file_path, local_file_path)
            
            if result.status == 200:
                print(f"文件 {oss_file_path} 下载成功，本地路径: {local_file_path}")
                return True
            else:
                print(f"文件下载失败，状态码: {result.status}")
                return False
                
        except OSSException as e:
            print(f"下载文件发生错误: {e}")
            return False
        except Exception as e:
            print(f"发生未知错误: {e}")
            return False