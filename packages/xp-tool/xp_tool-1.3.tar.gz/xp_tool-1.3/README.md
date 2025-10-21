# RAG Knowledge Base & AI Toolkit

这是一个功能强大的Python工具包，集成了RAG（检索增强生成）知识库构建、AI模型调用、云存储操作和数据处理等多种功能。特别适用于需要结合外部知识（如数据库Schema、业务文档）的智能对话和数据管理场景。

## 🚀 核心功能

### 1. RAG知识库系统 (P_RAGKnowledgeBase)

基于检索增强生成架构的知识库管理系统，支持多种数据源构建向量数据库：

- **PDF文档处理**：自动提取PDF文本并分割为向量块
- **原始文本处理**：直接处理结构化或非结构化文本
- **数据库Schema构建**：将数据库表结构转换为可检索的知识
- **智能文本分割**：使用重叠分块保持上下文连贯性

### 2. AI模型调用 (CallAi & CallBailianApp)

支持多种AI服务接口的统一调用：

- **OpenAI兼容接口**：支持任何兼容OpenAI API的模型服务
- **阿里云百炼平台**：专为阿里云DashScope应用设计
- **RAG增强对话**：可结合知识库上下文生成更准确的回答
- **灵活的提示词管理**：支持动态修改系统提示词模板

### 3. 云存储集成 (OSSHandler)

阿里云OSS对象存储的便捷操作接口：

- **文件上传下载**：本地与OSS间的文件同步
- **Excel数据处理**：直接从OSS读取Excel文件为DataFrame
- **格式验证**：自动验证文件类型和存在性

### 4. 数据导出与邮件发送 (ExportToEmail)

将数据处理结果自动化发送：

- **Excel导出**：DataFrame自动转换为Excel格式
- **邮件发送**：支持HTML格式邮件和附件
- **临时文件管理**：自动清理生成的临时文件

### 5. 文本工具类 (TxtTool)

本地文本文件的便捷操作：

- **读写操作**：支持覆盖和追加模式
- **JSON处理**：JSON文件的读取和解析
- **文件指针操作**：灵活的文件位置控制

### 6. 数据库Schema构建 (construct_schema)

自动化生成数据库表结构的元数据：

- **智能DDL生成**：基于表结构自动生成建表语句
- **多格式输出**：同时生成JSON和文本格式的Schema文件
- **示例数据整合**：包含字段示例数据的完整表描述

## 🛠 安装与配置

### 环境要求

- Python 3.7+
- 依赖包安装：

```bash
pip install openai pandas oss2 python-dotenv sentence-transformers faiss-cpu PyPDF2 langchain dashscope
```

### 环境配置

创建 `.env` 文件配置必要的环境变量：

```env
# OpenAI配置（如使用）
OPENAI_API_KEY=your_openai_api_key
OPENAI_BASE_URL=your_base_url

# 阿里云OSS配置
ACCESS_KEY_ID=your_access_key_id
ACCESS_KEY_SECRET=your_access_key_secret
ENDPOINT=your_oss_endpoint
BUCKET_NAME=your_bucket_name

# 邮件服务配置
email_sender=your_email@163.com
email_password=your_smtp_password
```

## 📚 使用示例

### 1. 构建RAG知识库

```python
from xp_tool import P_RAGKnowledgeBase

# 从PDF构建知识库
kb = P_RAGKnowledgeBase(chunk_size=500, chunk_overlap=50)
kb.build_from_pdf("document.pdf")

# 从文本构建知识库
kb.build_from_text("你的文本内容...")

# 从数据库Schema构建知识库
kb.build_from_schema(schema_dict)
```

### 2. AI对话与检索增强

```python
from xp_tool import CallAi

# 初始化AI客户端
ai = CallAi(api_key="your_key", base_url="your_url", model="qwen-plus")

# 设置系统提示词
ai.prompt = "你是一个专业的数据库助手，请根据知识库回答问题。"

# 普通对话
response = ai.chat("什么是数据库索引？")

# 结合知识库的RAG对话
response = ai.chat("查询用户表的结构", kb=knowledge_base)
```

### 3. 云存储操作

```python
from xp_tool import OSSHandler

# 初始化OSS处理器
oss = OSSHandler()

# 上传文件到OSS
oss.upload_to_oss("local_data.xlsx", "oss/path/data.xlsx")

# 从OSS读取Excel为DataFrame
df = oss.get_excel_from_oss("oss/path/data.xlsx")
```

### 4. 数据导出与邮件发送

```python
from xp_tool import ExportToEmail

# 将DataFrame发送到邮箱
result = ExportToEmail(
    df=dataframe,
    receiver="recipient@example.com",
    subject="数据查询结果"
)

print(result["message"])  # 查看发送状态
```

### 5. 数据库Schema构建

```python
from xp_tool import construct_schema

# 构建数据库表Schema
schema_dict, schema_text = construct_schema(
    desc_path="table_desc.xlsx",      # 表结构文件
    sample_data_path="sample_data.xlsx", # 示例数据文件
    table_name="database.users",      # 完整表名
    documentation="用户信息表，包含系统所有注册用户的基本信息...", # 表描述
    API_KEY="your_openai_key",        # 可选：用于智能生成DDL
    BASE_URL="your_base_url"          # 可选：AI服务地址
)
```

## 🔧 核心类详解

### P_RAGKnowledgeBase

**主要方法：**
- `build_from_pdf(file_path)`: 从PDF文件构建向量知识库
- `build_from_text(text)`: 从原始文本构建知识库  
- `build_from_schema(schema)`: 从数据库Schema字典构建知识库

**参数说明：**
- `chunk_size`: 文本分块大小（默认500字符）
- `chunk_overlap`: 块间重叠字符数（默认50）
- `embedding_model_name`: 嵌入模型名称（默认'all-MiniLM-L6-v2'）

### CallAi

**主要方法：**
- `chat(text, kb=None)`: 发送对话请求，可选知识库增强
- `prompt`属性: 获取或设置系统提示词模板

**参数说明：**
- `api_key`: API认证密钥
- `base_url`: 服务基础地址
- `model`: 模型名称（默认'qwen-plus'）

### OSSHandler

**主要方法：**
- `upload_to_oss(local_path, oss_path)`: 上传文件到OSS
- `get_excel_from_oss(oss_path)`: 从OSS获取Excel为DataFrame
- `download_file(oss_path, local_path)`: 下载OSS文件到本地

## 🎯 应用场景

### 智能数据库助手
结合数据库Schema知识库，让AI理解表结构并生成准确的SQL查询。

### 文档问答系统
基于PDF文档构建知识库，实现智能文档检索和问答。

### 自动化数据报告
从数据库查询数据，自动生成Excel报告并通过邮件发送。

### 企业知识管理
整合企业文档、数据库Schema等资源，构建统一的知识检索平台。

## ⚠️ 注意事项

1. **API密钥安全**：确保妥善保管各类API密钥，建议使用环境变量管理
2. **文件路径验证**：所有文件操作前都会验证路径有效性
3. **错误处理**：各类操作都有完善的异常处理和错误提示
4. **资源清理**：临时文件会自动清理，避免磁盘空间占用
5. **网络连接**：云服务操作需要稳定的网络连接

## 🔄 扩展开发

本项目采用模块化设计，易于扩展：

- 添加新的AI服务客户端：继承基础AI类实现特定接口
- 支持新的文件格式：在相应处理器中添加格式解析逻辑
- 自定义知识库来源：实现新的`build_from_*`方法