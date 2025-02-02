from typing import TypedDict, Annotated, Union, Dict, Any
from langgraph.graph import Graph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# 定义状态类型
class AgentState(TypedDict):
    messages: Annotated[list[HumanMessage | AIMessage], "对话历史"]
    next: Annotated[str, "下一个节点"]

# 创建 LLM
def create_llm():
    return ChatOpenAI(temperature=0)

# 系统提示
SYSTEM_PROMPT = """你是一个专业的 AI 助手，特别擅长解释技术概念。以下是一些关键技术的准确定义：

LangChain：
- 这是一个用于开发 LLM（大语言模型）应用的框架
- 主要组件包括：Chains（链式调用）、Agents（智能代理）、Memory（记忆系统）、Prompts（提示管理）
- 用于构建复杂的 LLM 应用流程，如文档问答、对话系统等

LangGraph：
- 这是 LangChain 生态系统中的一个工具
- 用于构建和管理多步骤、多代理的 LLM 应用工作流
- 提供了图形化的方式来组织和管理复杂的 LLM 交互流程

请基于这些准确的定义来回答用户的问题。"""

# 处理用户输入
def user_message(state: Dict[str, Any]) -> Dict[str, Any]:
    messages = state.get("messages", [])
    if not messages:
        # 如果是新对话，添加系统提示
        messages.append(SystemMessage(content=SYSTEM_PROMPT))
    
    message = state.get("message", "")
    messages.append(HumanMessage(content=message))
    return {"messages": messages, "next": "ai_response"}

# AI 响应
def ai_response(state: Dict[str, Any]) -> Dict[str, Any]:
    llm = create_llm()
    response = llm.invoke(state["messages"])
    messages = state["messages"]
    messages.append(response)
    # 一轮对话后结束
    return {"messages": messages, "next": END}

# 创建图
def build_graph():
    # 创建工作流程图
    workflow = Graph()

    # 添加节点
    workflow.add_node("user_message", user_message)
    workflow.add_node("ai_response", ai_response)

    # 设置边
    workflow.add_edge("user_message", "ai_response")
    workflow.add_edge("ai_response", END)

    # 设置入口
    workflow.set_entry_point("user_message")

    return workflow.compile()

# 导出图实例
graph = build_graph()
