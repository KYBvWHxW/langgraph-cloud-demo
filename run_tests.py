import os
from langsmith import Client
from langchain.callbacks.tracers import LangChainTracer
from main import build_graph

# 设置环境变量
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "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"
os.environ["LANGCHAIN_PROJECT"] = "simple_chat_agent"

def run_test(message, test_name):
    print(f"\n运行测试: {test_name}")
    print(f"输入: {message}")
    
    # 初始化追踪器
    tracer = LangChainTracer(project_name="simple_chat_agent")
    
    # 获取图实例
    graph = build_graph()
    
    # 运行测试
    messages = []
    result = graph.invoke(
        {"messages": messages, "message": message},
        config={
            "callbacks": [tracer],
            "metadata": {"test_name": test_name}
        },
    )
    
    # 提取 AI 的回复
    ai_message = result["messages"][-1].content
    print(f"AI 回复: {ai_message}")
    print("-" * 50)
    
    return result

# 测试用例
test_cases = [
    {
        "name": "基础问候测试",
        "message": "你好，请介绍一下你自己。"
    },
    {
        "name": "LangChain 技术测试",
        "message": "LangChain 是一个用于构建 LLM 应用的框架，请详细解释它的主要组件和用途。"
    },
    {
        "name": "LangGraph 技术测试",
        "message": "什么是 LangGraph？它和 LangChain 有什么关系？"
    },
    {
        "name": "数学计算测试",
        "message": "如果一个房间长 6 米，宽 4 米，请计算它的面积。"
    },
    {
        "name": "创意写作测试",
        "message": "请写一个关于春天的短诗。"
    },
    {
        "name": "知识问答测试",
        "message": "请介绍一下人工智能的主要应用领域。"
    },
    {
        "name": "系统设计测试",
        "message": "如何设计一个高可用的微服务架构？请从可扩展性、容错性和性能方面详细说明。"
    },
    {
        "name": "问题解决测试",
        "message": "在一个大型项目中，如何有效地进行代码重构以提高可维护性？"
    }
]

def main():
    print("开始运行测试套件...")
    
    for test_case in test_cases:
        try:
            run_test(test_case["message"], test_case["name"])
        except Exception as e:
            print(f"测试 '{test_case['name']}' 失败: {str(e)}")
    
    print("\n所有测试完成！")

if __name__ == "__main__":
    main()
