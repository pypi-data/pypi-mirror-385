from openai import OpenAI
from http import HTTPStatus
from dashscope import Application
import dashscope
from .rag_knowledge_base import P_RAGRetriever


class CallAi:
    """
    基于OpenAI兼容接口的AI调用类，支持RAG（检索增强生成）功能，
    可加载知识库上下文辅助回答，并提供prompt模板的持久化存储。
    适用于需要结合外部知识（如数据库Schema、业务文档）的对话场景。
    """
    def __init__(self,api_key,base_url,model=None,name=None):
        """
        初始化AI调用客户端，配置API连接信息、模型参数及prompt存储
        
        参数:
            api_key (str): 用于API身份验证的密钥
            base_url (str): OpenAI兼容接口的基础URL（如自定义模型服务地址）
            model (str, 可选): 调用的模型名称，默认使用'qwen-plus'
        
        属性说明:
            client: OpenAI客户端实例，用于发送API请求
        """
        self.api_key = api_key
        self.base_url = base_url
        self.client = OpenAI(
            api_key = api_key,
            base_url= base_url,
        )
        self.model =  model if model else 'qwen-plus'
        self._prompt = ''

    @property
    def prompt(self):
        """
        系统提示词模板的访问器（getter）
        返回当前存储的prompt内容，用于查看或调试
        """
        return self._prompt

    @prompt.setter
    def prompt(self,content):
        """
        系统提示词模板的修改器（setter）
        
        参数:
            content (str): 新的系统提示词模板内容
        """
        self._prompt = content

    def chat(self,text,top_p = 0.9, temperature = 0.7,kb=None,top_k=3):
        """
        核心对话方法：结合RAG检索增强生成回答，支持动态加载知识库上下文
        
        参数:
            text (str): 用户输入的查询文本（问题或指令）
            top_p (float, 可选): 模型采样参数（0-1），控制输出多样性，默认0.9
            temperature (float, 可选): 模型温度参数（0-1），值越高输出越随机，默认0.7
            kb (P_RAGKnowledgeBase实例, 可选): 知识库实例，用于检索相关上下文
        
        流程说明:
            1. 若传入知识库（kb），则通过P_RAGRetriever检索与查询相关的文本块
            2. 将检索到的上下文整合到系统提示词中（_prompt_copy）
            3. 调用AI模型，传入系统提示词和用户查询，生成回答
            4. 若检索失败（如kb未初始化），则仅使用原始系统提示词
        
        返回:
            str: AI生成的回答文本
        """
        self.kb = kb
        try:
            retriever = P_RAGRetriever(self.kb, self.client, top_k)
            relevant_indices = retriever.retrieve(text)
            # 获取相关文本块（需要保存文本块引用）
            context = "\n".join([self.kb.chunks[i] for i in relevant_indices])
            self._prompt_copy = self._prompt
            self._prompt_copy += f'''# 知识库 请记住以下材料，他们可能对回答问题有帮助。{context}'''
        except Exception as e:
            self._prompt_copy = self._prompt
        completion = self.client.chat.completions.create(
        model= self.model,
        messages=[
                {'role': 'system', 'content': f'{self._prompt_copy}'},
                {'role': 'user', 'content': text}],
            temperature = temperature,
            top_p = top_p
        )
        reply = completion.choices[0].message.content
        return reply

class CallBailianApp:
    """
    阿里云百炼（DashScope）应用调用类，用于与部署在百炼平台的应用进行交互。
    以流式（增量）方式获取应用响应，适用于需要实时展示生成结果的场景（如对话交互）。
    """
    def __init__(self,api_key,app_id,biz_params={},model=None):
        """
        初始化百炼应用调用实例
        
        参数:
            api_key (str): 阿里云DashScope API密钥，用于身份验证
            app_id (str): 百炼平台上部署的应用ID，指定要调用的目标应用
            biz_params (dict, 可选): 业务参数字典，用于向应用传递额外的业务配置（如角色设定、格式约束等）
            model (str, 可选): 模型标识（预留参数，部分应用可能需要指定具体模型）
        """
        self.api_key = api_key
        self.app_id = app_id
        self.biz_params =biz_params
        
    def chat(self,message):
        """
        向百炼应用发送消息并以流式方式获取响应
        
        参数:
            message (str): 发送给应用的输入消息（提示词/prompt）
        
        功能说明:
            1. 调用百炼Application API，以流式（stream=True）和增量输出（incremental_output=True）模式发送请求
            2. 实时接收应用返回的响应片段，逐段打印结果
            3. 若请求失败，打印错误信息（包括request_id、状态码、错误描述）
        
        """
        response = Application.call(
            api_key=self.api_key,
            app_id=self.app_id,# 替换为实际的应用 ID
            prompt=message,
            biz_params=self.biz_params
            )
        if response.status_code != HTTPStatus.OK:
            print(f'request_id={response.request_id}')
            print(f'code={response.status_code}')
            print(f'message={response.message}')
            print(f'请参考文档：https://www.alibabacloud.com/help/zh/model-studio/developer-reference/error-code')
        else:
            print(f'{response.output.text}\n')