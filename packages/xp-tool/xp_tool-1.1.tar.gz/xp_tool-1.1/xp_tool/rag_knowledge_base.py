from openai import OpenAI
import string
import random
import pandas as pd
import PyPDF2
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

class P_RAGKnowledgeBase:
    """
    基于RAG（Retrieval-Augmented Generation）架构的知识库类，用于构建和管理文本向量数据库。
    支持从PDF文件、原始文本或结构化Schema数据构建知识库，提供相似性检索功能，
    可用于辅助大模型生成更准确的回答（如数据库操作、文档问答等场景）。
    """
    
    def __init__(self, chunk_size=500,chunk_overlap=50,embedding_model_name='all-MiniLM-L6-v2'):
        """
        初始化RAG知识库实例
        
        参数:
            chunk_size: 文本分割的块大小（字符数），默认500
            chunk_overlap: 文本块之间的重叠字符数，默认50（用于保持上下文连贯性）
            embedding_model_name: 用于生成文本向量的模型名称，默认使用'all-MiniLM-L6-v2'
        """
        self.embedding_model = SentenceTransformer(embedding_model_name) #将文本转换为向量表示的模型
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        ) #定义文本分割器
        self.vector_db = None
        self.chunks = []
    
    def build_from_pdf(self, file_path):
        """
        从PDF文件构建知识库：提取PDF文本→分割→生成向量→存储到向量数据库
        
        参数:
            file_path: PDF文件的路径（字符串）
        """
        # PDF提取文本
        text = self._extract_text_from_pdf(file_path)
        # 分割文本块
        self.chunks  = self.text_splitter.split_text(text)
        # 生成嵌入向量
        embeddings = self.embedding_model.encode(self.chunks)
        # 创建向量数据库
        dimension = embeddings.shape[1]
        self.vector_db = faiss.IndexFlatL2(dimension)
        self.vector_db.add(np.array(embeddings).astype('float32'))
        print(f"向量数据库构建完成，包含 {self.vector_db.ntotal} 个向量")
        
    def _extract_text_from_pdf(self, file_path):
        """
        从PDF文件中提取文本内容（私有辅助方法）
        
        参数:
            file_path: PDF文件的路径（字符串）
        
        返回:
            提取的文本内容（字符串）
        """
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text()
        return text

    def build_from_text(self,text):
        """
        从原始文本直接构建知识库：分割文本→生成向量→存储到向量数据库
        
        参数:
            text: 原始文本内容（字符串），如结构化文档、Schema描述等
        """
        if not text or not text.strip():
            print("输入的文本为空，无法构建知识库")
            return
        # 分割文本块并构建知识库
        self._process_text(text)
        
    def _process_text(self, text):
        """
        处理文本的通用方法（私有辅助方法）：
        1. 将文本分割为指定大小的块
        2. 生成文本块的向量嵌入
        3. 创建并初始化FAISS向量数据库
        
        参数:
            text: 待处理的原始文本（字符串）
        """
        # 分割文本块
        self.chunks = self.text_splitter.split_text(text)
        print(f"文本分割完成，共得到 {len(self.chunks)} 个文本块")
        
        # 生成嵌入向量
        embeddings = self.embedding_model.encode(self.chunks)
        
        # 创建向量数据库
        dimension = embeddings.shape[1]
        self.vector_db = faiss.IndexFlatL2(dimension)
        self.vector_db.add(np.array(embeddings).astype('float32'))
        print(f"向量数据库构建完成，包含 {self.vector_db.ntotal} 个向量")

    def build_from_schema(self,schema:dict):
        """
        从结构化Schema字典构建知识库：
        将数据库表结构（包含表名、描述、字段信息、示例数据等）转换为自然语言文本，
        再通过通用文本处理流程构建向量数据库，便于后续检索表结构规则。
        
        参数:
            schema: 包含数据库表结构的字典，格式需符合：
                {
                    "schema_id": str,
                    "tables": [
                        {
                            "table_name": str,
                            "documentation": str,
                            "ddl": str,
                            "columns": [{"name": str, "column_value": str, "sample_data": list}, ...]
                        },
                        ...
                    ],
                    "row_sample": str
                }
        """
        schema_id = schema['schema_id']
        table_name = schema['tables'][0]['table_name']
        documentation = schema['tables'][0]['documentation']
        ddl = schema['tables'][0]['ddl']
        column = ""
        for i in schema['tables'][0]['columns']:
            column += f"- {i['name']}:{i['column_value']}。 示例：{'、'.join(str(x) for x in i['sample_data'])}\n"
        row_sample = schema['row_sample']
        total_schema = f"""
        \n
        schema_id：{schema_id}
        表名：{table_name}
        表描述和查数注意事项：
        {documentation}
        建表语句：
        {ddl}
        字段信息：
        {column}
        示例数据：
        {row_sample}
        \n
        """
        self._process_text(total_schema)

class P_RAGRetriever:
    """
    RAG（Retrieval-Augmented Generation）架构中的检索器类，
    负责将用户查询转换为向量，并从知识库的向量数据库中检索最相关的文本块索引。
    检索结果可用于辅助大模型生成更准确的回答。
    """
    def __init__(self, knowledge_base, openai_client, top_k=3):
        """
        初始化检索器实例
        
        参数:
            knowledge_base: 已构建的知识库实例（如P_RAGKnowledgeBase），需包含向量数据库和嵌入模型
            openai_client: OpenAI客户端实例（当前未在检索逻辑中使用，可用于后续扩展）
            top_k: 检索返回的最相关文本块数量，默认3
        """
        self.knowledge_base = knowledge_base
        self.client = openai_client
        self.top_k = top_k

    def retrieve(self, query):
        """
        根据查询检索知识库中最相关的文本块索引
        
        参数:
            query: 用户查询文本（字符串）
        
        返回:
            最相关的文本块索引列表（整数列表），对应知识库中chunks的索引
        """
        # 将查询转换为向量
        query_embedding = self.knowledge_base.embedding_model.encode([query])

        # 在向量数据库中搜索
        distances, indices = self.knowledge_base.vector_db.search(
            np.array(query_embedding).astype('float32'),
            self.top_k
        )

        if isinstance(indices, np.ndarray):
            if indices.ndim > 1:
                return indices[0].tolist()  
            else:
                return indices.tolist()     
        else:
            return indices.tolist() if hasattr(indices, 'tolist') else list(indices)