# MCP ChatBot项目
能够实现MCP调用的对话机器人

## 接口梳理

- [x] 创建MCP Server
- [x] 删除MCP Server
- [x] 更新MCP Server
- [x] 查询 MCP Server列表
- [x] 查询 MCP Server的详情
- [x] 启用/停用MCP Server(让大模型更加精准的找到需要调用的函数)
- [x] 刷新MCP Server的在线状态（相当于重启或重新连接MCP Server）
- [x] 查询MCP Server的tools列表（直接通过配置获取）
- [x] 调用MCP Server的tool

> 支持 stdio + sse + stremable http


## 服务部署

### 命令行运行(对stdio友好)

```
uv pip install -e .
mcp-chatbot
```

### 容器部署（对sse和streamable http友好）

构建镜像
```
docker build -t mcp-chatbot:v1 .
```

启动容器
```
docker run -d --name mcp-chatbot --restart always \
-p8088:8000 \
-v/Users/morris/Desktop/coding/mcp-chatbot/mcp_chatbot.db:/app/mcp_chatbot.db \
mcp-chatbot:v1
```