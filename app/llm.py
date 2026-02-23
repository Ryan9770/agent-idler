import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

load_dotenv(dotenv_path="../.env") # 루트의 .env 로드

# 5070 Ti의 성능을 믿고 모델들을 세팅합니다.
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

planner_llm = ChatOllama(model=os.getenv("MODEL_PLANNER", "phi4"), base_url=OLLAMA_URL)
executor_llm = ChatOllama(model=os.getenv("MODEL_EXECUTOR", "qwen2.5-coder:7b"), base_url=OLLAMA_URL)
reviewer_llm = ChatOllama(model=os.getenv("MODEL_REVIEWER", "deepseek-coder-v2"), base_url=OLLAMA_URL)