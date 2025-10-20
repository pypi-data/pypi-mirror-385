# Excel 与 OSS 处理工具库

这是xp的私人工具库。

## 功能特性

### 🤖 AI 对话功能 (CallAi 类)
- 支持 OpenAI 兼容的 API 调用
- 可自定义系统提示词和模型参数
- 灵活的对话配置（temperature、top_p）

### ☁️ OSS 文件管理 (ExcelOSSHandler 类)
- Excel 文件上传到阿里云 OSS
- 从 OSS 下载 Excel 文件并转换为 pandas DataFrame
- 完整的错误处理和文件验证

### 📧 数据导出与邮件发送
- 将 DataFrame 导出为 Excel 文件
- 自动通过邮件发送 Excel 附件
- 支持 HTML 格式的邮件内容

## 安装依赖

```bash
pip install openai pandas oss2 python-dotenv openpyxl
```

## 快速开始

### 1. AI 对话功能

```python
from your_module import CallAi

# 初始化 AI 客户端
ai = CallAi(
    api_key="your-api-key",
    base_url="https://api.openai.com/v1",
    model="qwen-plus"  # 默认模型
)

# 设置系统提示词
ai.prompt = "你是一个有用的助手"

# 进行对话
response = ai.chat("你好，请介绍一下自己")
print(response)
```

### 2. OSS 文件管理

```python
from your_module import ExcelOSSHandler

# 初始化 OSS 处理器
oss_handler = ExcelOSSHandler(
    access_key_id="your-access-key-id",
    access_key_secret="your-access-key-secret",
    endpoint="https://oss-cn-hangzhou.aliyuncs.com",
    bucket_name="your-bucket-name"
)

# 上传 Excel 文件到 OSS
success = oss_handler.upload_excel_to_oss(
    local_file_path="local_file.xlsx",
    oss_file_path="oss/path/file.xlsx"
)

# 从 OSS 下载 Excel 并转换为 DataFrame
df = oss_handler.get_excel_from_oss("oss/path/file.xlsx")
```

### 3. 数据导出与邮件发送

```python
from your_module import export_to_excel_and_email
import pandas as pd

# 创建示例数据
df = pd.DataFrame({
    'Name': ['Alice', 'Bob', 'Charlie'],
    'Age': [25, 30, 35],
    'City': ['Beijing', 'Shanghai', 'Guangzhou']
})

# 导出数据并发送邮件
result = export_to_excel_and_email(
    df=df,
    receiver="recipient@example.com",
    subject="数据导出报告",
    sender="your-email@163.com",
    password="your-email-password"
)

print(result)
```

## 环境变量配置

创建 `.env` 文件来管理敏感信息：

```env
# OpenAI 配置
OPENAI_API_KEY=your-openai-api-key
OPENAI_BASE_URL=https://api.openai.com/v1

# 阿里云 OSS 配置
OSS_ACCESS_KEY_ID=your-access-key-id
OSS_ACCESS_KEY_SECRET=your-access-key-secret
OSS_ENDPOINT=oss-cn-hangzhou.aliyuncs.com
OSS_BUCKET_NAME=your-bucket-name

# 邮件配置
email_sender=your-email@163.com
email_password=your-email-authorization-code
```

## API 参考

### CallAi 类

#### 初始化参数
- `api_key`: OpenAI API 密钥
- `base_url`: API 基础地址
- `model`: 模型名称（默认：'qwen-plus'）

#### 方法
- `chat(text, top_p=0.9, temperature=0.7)`: 发送对话请求

### ExcelOSSHandler 类

#### 初始化参数
- `access_key_id`: 阿里云访问密钥 ID
- `access_key_secret`: 阿里云访问密钥 Secret
- `endpoint`: OSS 服务端点
- `bucket_name`: 存储桶名称

#### 方法
- `upload_excel_to_oss(local_file_path, oss_file_path)`: 上传 Excel 文件
- `get_excel_from_oss(oss_file_path)`: 下载并转换 Excel 文件为 DataFrame

### ExportToEmail函数

#### 参数
- `df`: 要导出的 pandas DataFrame
- `receiver`: 收件人邮箱地址（默认：'xupeng23456@126.com'）
- `subject`: 邮件主题
- `sender`: 发件人邮箱
- `password`: 发件人邮箱密码/授权码

#### 返回值
返回包含操作结果的字典：
```python
{
    "status": "success" | "failed",
    "message": "描述信息",
    "file_path": "临时文件路径",
    "email_sent": True | False,
    "row_count": 数据行数,
    "timestamp": "时间戳"
}
```

## 注意事项

1. **文件格式**: 仅支持 `.xlsx` 和 `.xls` 格式的 Excel 文件
2. **邮件服务**: 默认使用 163 邮箱的 SMTP 服务，如需使用其他邮箱请修改 SMTP 配置
3. **临时文件**: 导出的 Excel 文件会在邮件发送成功后自动清理
4. **错误处理**: 所有操作都包含完整的异常捕获和错误信息返回

## 错误排查

### 常见问题

1. **OSS 连接失败**
   - 检查 Access Key 和 Secret 是否正确
   - 确认 endpoint 和 bucket name 是否正确

2. **邮件发送失败**
   - 确认发件人邮箱密码/授权码是否正确
   - 检查 SMTP 服务器和端口配置
   - 确认网络连接正常

3. **Excel 文件处理错误**
   - 确认文件路径正确且文件存在
   - 检查文件是否被其他程序占用
   - 验证文件格式是否为支持的 Excel 格式

## 许可证

此项目基于 MIT 许可证开源。