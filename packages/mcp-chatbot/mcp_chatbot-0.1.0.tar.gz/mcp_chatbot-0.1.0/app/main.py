import asyncio
import json
import sys
import os
from typing import List
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

# 添加项目根目录到Python路径
# sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.mymcp import MCPClient
from app.schemas import CallToolRequest, ConnectionCfg, MCPServerCreate, MCPServerResponse, MCPServerWithStatusResponse
from app.config import settings
from sqlalchemy.orm import Session
from app.database import SessionLocal,engine
from fastapi.security import APIKeyHeader
from app.orm import *
from app.models import Base
from fastapi import Security,HTTPException,BackgroundTasks, FastAPI,Depends,APIRouter
Base.metadata.create_all(bind=engine)
api_key_security = APIKeyHeader(name="Authorization")
mcp_clients:dict[int,MCPClient] = {}
async def connect_and_cache_client(mcp_server:MCPServer)->bool:
    if mcp_server.id in mcp_clients:
        client = mcp_clients[mcp_server.id]
        try:
            await client.ping()
            return True
        except Exception as e:
            print(f"MCP Server {mcp_server.id} is offline {e}")
            return False
    else:
        try:
            server_params = json.loads(mcp_server.cfg)
            client = MCPClient(server_params,mcp_server.protocol)
            try:
                await asyncio.wait_for(client.connect_to_server(),timeout=5)
            except asyncio.TimeoutError:
                print(f"Timeout: MCP Server {mcp_server.id} connect_to_server took too long")
                return False
            await client.ping()
            mcp_clients[mcp_server.id] = client
            return True
        except Exception as e:
            print(f"MCP Server {mcp_server.id} is offline {e}")
            return False
def verify_api_key(authorization: str = Security(api_key_security)):
    scheme,_,token = authorization.partition(" ")
    if scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authentication scheme")
    if token != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return token
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
app = FastAPI()
app_router = APIRouter(prefix="/api")
# 添加CORS中间件解决跨域问题
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
@app.get('/api/test')
async def read_root(api_key: str = Depends(verify_api_key)):
    return {"message":1234}
# 创建MCP Server
@app_router.post("/mcp_server",response_model=MCPServerResponse)
async def create_mcp_server(mcp_server_create: MCPServerCreate,db: Session = Depends(get_db),api_key: str = Depends(verify_api_key)):
    existing_mcp_server = get_mcp_server_db(db,mcp_server_create.name)
    if existing_mcp_server:
        raise HTTPException(status_code=400, detail="MCP server with this name already exists")
    created_mcp_server = create_mcp_server_db(db,mcp_server_create)
    return created_mcp_server

# 查询MCP Server详情
@app_router.get("/mcp_server/{mcp_server_id}",response_model=MCPServerResponse)
async def get_mcp_server(mcp_server_id: int,db: Session = Depends(get_db),api_key: str = Depends(verify_api_key)):
    mcp_server = get_mcp_server_by_id_db(db,mcp_server_id)
    if not mcp_server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    return mcp_server

# 查询MCP Server列表
@app_router.get("/mcp_server",response_model=List[MCPServerWithStatusResponse])
async def get_mcp_server_list(db: Session = Depends(get_db),api_key: str = Depends(verify_api_key),background_tasks: BackgroundTasks = BackgroundTasks()):
    mcp_server_list = get_mcp_server_list_db(db)
    mcp_server_list_with_status:List[MCPServerWithStatusResponse] = []
    for mcp_server in mcp_server_list:
        is_online = False
        if mcp_server.id in mcp_clients:
            client = mcp_clients[mcp_server.id]
            try:
                await client.ping()
                is_online = True
            except Exception as e:
                is_online = False
        else:
            background_tasks.add_task(connect_and_cache_client,mcp_server)
        mcp_server_with_status = MCPServerWithStatusResponse.model_validate(mcp_server)
        mcp_server_with_status.is_online = is_online
        if is_online:
            tools = await mcp_clients[mcp_server.id].list_tools()
            mcp_server_with_status.tools = tools
        mcp_server_list_with_status.append(mcp_server_with_status)
    return mcp_server_list_with_status  

# 更新MCP Server
@app_router.put("/mcp_server/{mcp_server_id}",response_model=MCPServerResponse)
async def update_mcp_server(mcp_server_id:int,mcp_server_update:MCPServerUpdate, db: Session = Depends(get_db),api_key: str = Depends(verify_api_key)):
    mcp_agent = get_mcp_server_by_id_db(db, mcp_server_id)
    if not mcp_agent:
        raise HTTPException(status_code=404, detail="MCP agent not found")
    updated_mcp_agent = update_mcp_server_db(db, mcp_server_id, mcp_server_update)
    return updated_mcp_agent

# 删除MCP Server
@app_router.delete("/mcp_server/{mcp_server_id}",response_model=MCPServerResponse)
async def delete_mcp_server(mcp_server_id: int,db: Session = Depends(get_db),api_key: str = Depends(verify_api_key)):
    mcp_server = get_mcp_server_by_id_db(db,mcp_server_id)
    if not mcp_server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    delete_mcp_server_db(db,mcp_server_id)
    return mcp_server

# 启用/停用MCP Server
@app_router.put("/mcp_server/{mcp_server_id}/toggle",response_model=MCPServerResponse)
async def toggle_mcp_server(mcp_server_id: int,db: Session = Depends(get_db),api_key: str = Depends(verify_api_key)):
    mcp_server = toggle_mcp_server_db(db,mcp_server_id)
    if not mcp_server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    return mcp_server

# 刷新MCP Server的在线状态
@app_router.put("/mcp_server/{mcp_server_id}/refresh",response_model=dict)
async def refresh_mcp_server(mcp_server_id: int,db: Session = Depends(get_db),api_key: str = Depends(verify_api_key)):
    mcp_server = get_mcp_server_by_id_db(db,mcp_server_id)
    if not mcp_server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    # 用client连接mcp server
    is_online = await connect_and_cache_client(mcp_server)
    return {
        "is_online":is_online
    }
# 获取MCP Server的工具列表
@app_router.post("/mcp_server/list_tools")
async def list_tools(con_cfg: ConnectionCfg,db: Session = Depends(get_db),api_key: str = Depends(verify_api_key)):
    try:
        server_params = json.loads(con_cfg.cfg)
        protocol = con_cfg.protocol
        client = MCPClient(server_params,protocol)
        await client.connect_to_server()
        tools = await client.list_tools()
        return tools
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")
    
# 工具调用实现
@app_router.post("/mcp_server/call_tool")
async def call_tool(call_tool_request: CallToolRequest,db: Session = Depends(get_db),api_key: str = Depends(verify_api_key)):
    tool_name = call_tool_request.name
    tool_arguments = json.loads(call_tool_request.arguments)
    parts = tool_name.split("/")
    if len(parts) < 2:
        raise HTTPException(status_code=400, detail="Invalid tool name")
    mcp_server_name = parts[0]
    tool_name = parts[1]
    mcp_server = get_mcp_server_by_name_db(db,mcp_server_name)
    if not mcp_server:
        raise HTTPException(status_code=404, detail="MCP server not found")
    try:
        client = mcp_clients[mcp_server.id]
        result = await client.call_tool(tool_name,tool_arguments)
        return result
    except Exception as e:
        print(f"Failed to call tool {tool_name} {e}")
        raise HTTPException(status_code=500, detail=f"Failed to call tool {tool_name}")
app.include_router(app_router)
if __name__ == "__main__":
    uvicorn.run(app,host="0.0.0.0",port=8000)
