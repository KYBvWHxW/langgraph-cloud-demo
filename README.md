# LangGraph Cloud Demo
# (LangGraph Cloud Application Example)

这是一个简单的 LangGraph 应用示例，用于部署到 LangChain 云平台。

## 功能

- 实现了一个简单的对话代理
- 使用 LangGraph 管理对话流程
- 支持云端部署

## 部署步骤

1. 安装 LangGraph CLI：
```bash
pip install langgraph
```

2. 登录到 LangSmith：
```bash
langgraph login
```

3. 部署应用：
```bash
langgraph deploy
```

## 环境变量

需要设置以下环境变量：
- OPENAI_API_KEY：OpenAI API 密钥
- LANGCHAIN_API_KEY：LangSmith API 密钥

## 使用方法

部署后，可以通过 LangSmith 界面访问和测试应用。
