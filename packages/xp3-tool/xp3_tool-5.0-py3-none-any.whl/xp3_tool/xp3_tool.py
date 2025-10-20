from openai import OpenAI
import string
import random
import os
import io
import pandas as pd
import oss2
from oss2.exceptions import ClientError
from typing import Optional
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import traceback
import logging
import tempfile
import atexit
import smtplib
import shutil

def uuid(length=16):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

class CallAi:
    def __init__(self,api_key,base_url,model=None):
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(
            api_key = api_key,
            base_url= base_url,
        )
        self.model =  model if model else 'qwen-plus'
        self._prompt = ""
        self.inquiry = ""

    @property
    def prompt(self):
        return self._prompt

    @prompt.setter
    def prompt(self,content):
        self._prompt = content

    def chat(self,text,top_p = 0.9, temperature = 0.7):
        completion = self.client.chat.completions.create(
            model= self.model,
            messages=[
                {'role': 'system', 'content': f'{self._prompt}'},
                {'role': 'user', 'content': text}],
            temperature = temperature,
            top_p = top_p
        )
        reply = completion.choices[0].message.content
        return reply

class ExcelOSSHandler:
    """处理Excel文件与阿里云OSS的交互，并提供转换为pandas DataFrame的功能"""
    
    def __init__(self, access_key_id: str, access_key_secret: str, endpoint: str, bucket_name: str):
        """
        初始化OSS连接
        
        :param access_key_id: 阿里云访问密钥ID
        :param access_key_secret: 阿里云访问密钥Secret
        :param endpoint: OSS服务的访问域名
        :param bucket_name: OSS存储桶名称
        """
        # 初始化OSS认证
        self.auth = oss2.Auth(access_key_id, access_key_secret)
        # 获取存储桶对象
        self.bucket = oss2.Bucket(self.auth, endpoint, bucket_name)
        
    def upload_excel_to_oss(self, local_file_path: str, oss_file_path: str) -> bool:
        """
        将本地Excel文件上传到OSS
        
        :param local_file_path: 本地Excel文件路径
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

def ExportToEmail(df, receiver = 'xupeng23456@126.com', subject: str = None,sender: str = None, password: str = None):
    if not password:
        load_dotenv()
        password = os.getenv("email_password")
        sender = os.getenv("email_sender")
    
    TEMP_DIR = "./temp"
    os.makedirs(TEMP_DIR, exist_ok=True)
    try:
        # 生成 Excel 文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        excel_filename = f"rds_query_result_{timestamp}.xlsx"
        filepath = os.path.join(TEMP_DIR, excel_filename)

        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='查询结果', index=False)


        # 3. 发送邮件
        smtp_server = 'smtp.163.com'
        smtp_port = 465

        if not subject:
            subject = f"数据结果 - {timestamp}"

        msg = MIMEMultipart()
        msg['From'] = sender
        msg['To'] = receiver
        msg['Subject'] = subject

        body = f"""
        <html>
          <body>
            <h2>📊 数据结果已导出</h2>
            <p>导出时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>数据已附在邮件中，请查收。</p>
          </body>
        </html>
        """
        msg.attach(MIMEText(body, 'html', 'utf-8'))

        with open(filepath, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f'attachment; filename="{excel_filename}"'
        )
        msg.attach(part)

        try:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server.login(sender, password)
            server.sendmail(sender, receiver, msg.as_string())
            server.quit()
            email_sent = True
            os.remove(filepath)
        except Exception as e:
            email_sent = False
            traceback.print_exc()

        return {
            "status": "success",
            "message": f"查询成功，Excel 已生成并发送至 {receiver}。",
            "file_path": filepath,
            "email_sent": email_sent,
            "row_count": len(df),
            "timestamp": timestamp
        }

    except Exception as e:
        traceback.print_exc()
        return {
            "status": "failed",
            "message": str(e),
            "file_path": None,
            "email_sent": False
        }
    