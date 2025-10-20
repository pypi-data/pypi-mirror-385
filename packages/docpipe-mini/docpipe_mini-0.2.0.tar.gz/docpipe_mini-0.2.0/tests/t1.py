import warnings
import sys
import os
from openai import OpenAI
from mem0 import Memory
from mem0.configs.base import MemoryConfig
from mem0.embeddings.configs import EmbedderConfig
from mem0.llms.configs import LlmConfig
from mem0.graphs.configs import Neo4jConfig, GraphStoreConfig
from mem0.configs.vector_stores.qdrant import QdrantConfig
from mem0.vector_stores.configs import VectorStoreConfig


# 抑制 Qdrant 客户端关闭时的异常
warnings.filterwarnings("ignore", message=".*import of msvcrt halted.*")

# 重定向异常输出以抑制 Qdrant 客户端的异常
original_excepthook = sys.excepthook
def quiet_excepthook(type, value, traceback):
    if "msvcrt" in str(value) and "halted" in str(value):
        return  # 忽略这个特定的异常
    original_excepthook(type, value, traceback)

sys.excepthook = quiet_excepthook
API_KEY = "your-api-key"
BASE_URL = "your-base-url"
config = MemoryConfig(
   llm=LlmConfig(
       provider="openai",
       config={
           "model": "deepseek-chat",
           "api_key": 'sk-1e755ae1fb5e4e7a8bce058cd7b6584c',
           "openai_base_url": 'https://api.deepseek.com'
       }
   ),
   embedder=EmbedderConfig(
       provider="openai",
       config={
           "embedding_dims": 2560,
           "model": "doubao-embedding-text-240715",
           "api_key": '3a5c39ed-5bc8-4002-ba2c-c650ada1408d',
           "openai_base_url": 'https://ark.cn-beijing.volces.com/api/v3/'
       }
   ),
   vector_store=VectorStoreConfig(
       provider="qdrant",
       config=QdrantConfig(
            collection_name="mem0_collection",
            host="192.168.90.46",
            port=6333,
            embedding_model_dims=2560,
       ).model_dump()
   ),
   graph_store=GraphStoreConfig(
       provider="neo4j",
       config={
           "url": 'bolt://192.168.90.46:7687',
           "username": 'neo4j',
           "password": 'StrongPassword123'
       }
   )
)

mem0 = Memory(config=config)



from docpipe import XlsxSerializer

print("=== Testing XLSX Serializer with LoggingMixin ===")
# serializer = XlsxSerializer()
# serializer.configure_logging(
#       enable_performance_logging=True,
#       log_level="DEBUG"
#   )
# print("Starting data processing with custom headers...")
# with serializer.log_timing("data_processing", file="销售统计表.xlsx"):
#     chunk_count = 0
#     for chunk in serializer.iterate_chunks("tests\\excel\\销售统计表.xlsx", header_row=1):
#         chunk_count += 1
#         serializer.log_info(f"Processing chunk: {chunk.type} on page {chunk.page}")
#         print(chunk.metadata, chunk.text)
#         mem0.add(f'{chunk.text}', metadata=chunk.metadata, user_id='test')
from docpipe.loaders._xlsx import XlsxSerializer

serializer = XlsxSerializer()

file_path = "tests\\excel\\销售统计表.xlsx"
print(f"Testing with: {file_path}")

print("\n1. Testing header_row=1 (should extract actual Chinese headers):")
chunk_count = 0
for chunk in serializer.iterate_chunks(file_path, header_row=1):
    print(chunk)

    mem0.add(f'{chunk.text}', metadata=chunk.metadata, user_id='test')


# result = mem0.add(f'我叫张三，今年12，喜欢篮球',user_id='test',)
# result = mem0.add(f'李四，今年13，喜欢篮球,是张三的朋友',user_id='test',)
# result = mem0.add(f'张二，今年33，喜欢篮球,是张三的爸爸',user_id='test',)
# print("Memory added successfully!")
# print("Result:", result)
# s=mem0.search('张三是谁',user_id='test')
# print(s)
# 优雅地关闭客户端以避免异常
# if hasattr(mem0, 'vector_store') and hasattr(mem0.vector_store, 'client'):
#     try:
#         mem0.vector_store.client.close()
#     except:
#         pass
from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent,create_openai_tools_agent
from langchain_openai import ChatOpenAI
from langchain.tools import Tool
from langchain.prompts import PromptTemplate
llm=ChatOpenAI(
    base_url='https://api.deepseek.com',
    api_key='sk-1e755ae1fb5e4e7a8bce058cd7b6584c',
    model="deepseek-chat"
)

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import BaseTool
prompt = ChatPromptTemplate.from_messages([
SystemMessage(content="""You are a helpful travel agent AI..."""),
MessagesPlaceholder(variable_name="context"),
HumanMessage(content="{input}")
])



# class mem(BaseTool):
import json

def retrieve_context(query: str, user_id: str):
   memories = mem0.search(query, user_id='test')
   serialized_memories = json.dumps(memories)

   return [
       {"role": "system", "content": f"Relevant information: {serialized_memories}"},
       {"role": "user", "content": query}
   ]

def generate_response(input: str, context: list):
   chain = prompt | llm
   response = chain.invoke({"context": context, "input": input})
   return response.content

def chat_turn(user_input: str, user_id: str):
    context = retrieve_context(user_input, user_id)
    print(context)
    response = generate_response(user_input, context)
    # save_interaction(user_id, user_input, response)
    return response



if __name__ == "__main__":
    print("Welcome to your personal Travel Agent Planner!")
    user_id = "test"
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("Travel Agent: Thank you for using our service!")
            break
        response = chat_turn(user_input, user_id)
        print(f"Travel Agent: {response}")