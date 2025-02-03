from typing import Dict, TypedDict, Sequence, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 定义状态类型
class GraphState(TypedDict):
    messages: Sequence[BaseMessage]
    next: str

# 创建 OpenAI 聊天模型
model = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0
)

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

# 定义节点函数
def generate_response(state: GraphState) -> GraphState:
    """生成 AI 的回复"""
    # 如果是新对话，添加系统提示
    if not state["messages"]:
        state["messages"].append(SystemMessage(content=SYSTEM_PROMPT))
    
    # 调用 LLM
    response = model.invoke(state["messages"])
    # 添加到消息历史
    return {
        "messages": [*state["messages"], response],
        "next": "decide_next_step"
    }

def decide_next_step(state: GraphState) -> Literal["generate_response", "end"]:
    """决定下一步操作"""
    last_message = state["messages"][-1]
    
    # 如果最后一条消息是用户的，继续对话
    if isinstance(last_message, HumanMessage):
        return "generate_response"
    # 如果最后一条消息是 AI 的，结束对话
    return "end"

# 处理用户输入
def user_message(state: Dict[str, Any]) -> Dict[str, Any]:
    messages = state.get("messages", [])
    message = state.get("message", "")
    messages.append(HumanMessage(content=message))
    return {"messages": messages, "next": "generate_response"}

# 创建图
def build_graph() -> StateGraph:
    """构建对话图"""
    # 创建工作流
    workflow = StateGraph(GraphState)
    
    # 添加节点
    workflow.add_node("generate_response", generate_response)
    workflow.add_node("user_message", user_message)
    
    # 添加条件边
    workflow.add_conditional_edges(
        "decide_next_step",
        decide_next_step,
        {
            "generate_response": "generate_response",
            "end": END
        }
    )
    
    # 设置入口节点
    workflow.set_entry_point("user_message")
    
    return workflow

# 创建图实例
graph = build_graph().compile()
