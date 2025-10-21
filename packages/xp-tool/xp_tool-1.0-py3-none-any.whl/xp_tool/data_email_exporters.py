import string
import os
import pandas as pd
from dotenv import load_dotenv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import traceback
import smtplib


def ExportToEmail(df, receiver = 'xupeng23456@126.com', subject: str = None,sender: str = None, password: str = None):
    """
    将数据表以邮件形式发送给指定用户
    
    :param receiver: 收件人邮箱
    :param subject: 邮件主题。默认为空
    :param sender: 发送人邮箱。默认为空，当空值时自动从环境文件中获取配置。
    :param password: 发送人邮箱的smtp密码。默认为空，当空值时自动从环境文件中获取配置。
    :return: 发送状态的字典结果。
    """
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