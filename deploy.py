from langsmith import Client

client = Client()

# 创建新项目
project = client.create_project(
    project_name="simple_chat_agent"
)

print(f"Created project: {project.name} with ID: {project.id}")

# 上传代码
response = client.upload_project(
    project_id=project.id,
    directory="/home/windsurf_user/CascadeProjects/langgraph_cloud_demo"
)

print(f"Uploaded project: {response}")
