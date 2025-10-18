from pydantic import BaseModel

class CallToolRequest(BaseModel):
    name: str
    arguments: str

class MCPServerUpdate(BaseModel):
    desc: str
    cfg: str
    protocol: str

class ConnectionCfg(BaseModel):
    cfg: str
    protocol: str

class MCPServerCreate(BaseModel):
    name: str
    desc: str
    cfg: str
    protocol: str

class MCPServerResponse(MCPServerCreate):
    is_enabled: bool
    id: int

class MCPServerWithStatusResponse(MCPServerResponse):
    is_online: bool = False
    tools: list[dict] = []
    class Config:
        from_attributes = True

class MCPAgentCreate(BaseModel):
    name: str
    avatar: str = None
    desc: str = None
    system_prompt: str = None
    cfg: str = None
    mcp_server_ids: str = None
    model_name: str = None

class MCPAgentUpdate(BaseModel):
    name: str = None
    avatar: str = None
    desc: str = None
    system_prompt: str = None
    cfg: str = None
    mcp_server_ids: str = None
    model_name: str = None

class MCPAgentResponse(MCPAgentCreate):
    id: int
    class Config:
        from_attributes = True