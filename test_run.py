import os
from dotenv import load_dotenv
from main import graph

# 加载环境变量
load_dotenv()

def main():
    # 使用环境变量中的 API key
    messages = [
        {"role": "user", "content": "What is the capital of France?"}
    ]
    
    result = graph({"messages": messages})
    print("Response:", result["response"])

if __name__ == "__main__":
    main()
