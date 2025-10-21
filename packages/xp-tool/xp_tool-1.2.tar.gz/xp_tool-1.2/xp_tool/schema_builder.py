import json
import pandas as pd
from openai import OpenAI
from .call_ai import CallAi
from .txt_tool import TxtTool

def construct_schema(desc_path,sample_data_path,table_name,documentation,schema_id='',ddl='',API_KEY=None,BASE_URL=None):
    """
    在利用 MCP 让 AI 操作数据库时，根据表结构信息和示例数据生成表的元数据schema，并存储到本地项目根目录下，文件名为"表名_schema.json"，以便后续提供给ai，使其正确、高效地与数据库交互。
    
    :param desc_path: 本地表结构信息路径。在数据库中使用 `desc 表名` 语句获取表结构，并下载到本地。
    :param sample_data_path: 本地示例数据路径。在数据库中用limit筛选若干行示例数据，不要有空值，并下载到本地。
    :param table_name: 数据库中的表名（带上库名）。
    :param documentation: 撰写表的详细描述和查数注意事项，这对ai理解表的作用很重要。
    :param schema_id: schema_id。
    :param ddl: 建表语句，默认为""，若想让AI生成建表语句，则需要后续提供`API_KEY`和`BASE_URL`参数。
    :param API_KEY: OpenaAi的APIkey，用来智能生成建表语句。
    :param BASE_URL: OpenaAi的基础地址，用来智能生成建表语句。
    :return: 发送状态的字典结果。
    """
    dict_ = {}
    tables = []
    columns = []
    df_desc = pd.read_excel(f'{desc_path}')[['Column','Comment','Type']]
    df_sample_data = pd.read_excel(f'{sample_data_path}')
    md_str = df_sample_data.to_markdown(index=False)
    if API_KEY:
        desc_md = df_desc.to_markdown(index=False)
        obj = CallAi(API_KEY,BASE_URL)
        obj.prompt = """
# 角色
你是一位精通PostgreSQL DDL语句的数据库专家，负责根据用户提供的表结构Markdown和表名，准确写出精准的建表语句。你需要具备自主判断字段精度的能力，并在DDL语句中添加字段备注。

## 技能
### 技能 1: 编写建表语句
- 根据用户提供的表结构Markdown和表名，编写准确的建表语句。
- 对于`varchar`类型字段，默认使用varchar(255)作为精度。
- 在DDL语句中根据Markdown的内容为字段添加备注信息。

### 技能 2: 理解表结构
- 仔细阅读用户提供的表结构Markdown，确保理解每个字段的含义和数据类型。
- 如果用户提供的表结构不完整或有疑问，主动询问以获取更多信息。

### 技能 3: 调用工具
- 如果需要进一步的信息或验证某些细节，可以调用搜索工具或查询相关知识库。
- 使用工具时，确保获取的信息准确可靠，并将其应用到DDL语句中。

## 限制
- 仅根据用户提供的表结构Markdown和表名生成建表语句。
- 不输出任何多余的解释或注释，直接输出建表语句。
- 保持DDL语句的准确性和完整性，确保建表语句的易读性。
- 在编写DDL语句时，始终考虑最佳实践。
        """
        input_content= f"表结构的markdown: {desc_md}。表名：{table_name}"
        ddl = obj.chat(input_content)
    for i in range(df_desc.shape[0]):
        column_name = df_desc.iloc[i,0]
        if df_desc.iloc[i,2] == 'varchar':
            sample_data = [str(x) for x in df_sample_data[column_name].tolist()]
        else:
            sample_data = df_sample_data[column_name].tolist()
        columns.append(
            {
                "name":column_name,
                "column_value":df_desc.iloc[i,1],
                "sample_data":sample_data
            }
                      )
    dict_ = {
             "schema_id":schema_id,
             "tables":[
                 {
                "table_name":table_name,
                "documentation":documentation,
                "ddl":ddl,
                "columns":columns
                 }
         ],
             "row_sample":md_str
        }
    file_path_json = f"{table_name}_schema.json"
    file_path_txt = f"{table_name}_schema.txt"  
    try:
        with open(file_path_json, 'w', encoding='utf-8') as f:
            json.dump(dict_, f, ensure_ascii=False, indent=4)
        schema = dict_
        schema_id = schema['schema_id']
        table_name = schema['tables'][0]['table_name']
        documentation = schema['tables'][0]['documentation']
        ddl = schema['tables'][0]['ddl']
        column = ""
        for i in schema['tables'][0]['columns']:
            column += f"- {i['name']}:{i['column_value']}。 示例：{'、'.join(str(x) for x in i['sample_data'])}\n"
        row_sample = schema['row_sample']
        total_schema = f"""
        
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

        """
        TxtTool(file_path_txt).write(total_schema)
    except Exception as e:
        print(e)
    return dict_,total_schema