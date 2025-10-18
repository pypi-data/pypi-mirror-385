from app.schemas import MCPServerCreate,MCPServerUpdate
from app.models import MCPServer
from sqlalchemy.orm import Session
from app.schemas import MCPAgentCreate, MCPAgentUpdate
from app.models import MCPAgent

def get_mcp_server_db(db: Session, name: str):
    return db.query(MCPServer).filter(MCPServer.name == name).first()

def create_mcp_server_db(db: Session, mcp_server_create: MCPServerCreate):
    mcp_server = MCPServer(**mcp_server_create.model_dump())
    db.add(mcp_server)
    db.commit()
    db.refresh(mcp_server)
    return mcp_server

# 查询详情
def get_mcp_server_by_id_db(db: Session, mcp_server_id: int):
    return db.query(MCPServer).filter(MCPServer.id == mcp_server_id).first()

# 根据名称查询
def get_mcp_server_by_name_db(db: Session, name: str):
    return db.query(MCPServer).filter(MCPServer.name == name).first()

# 查询列表
def get_mcp_server_list_db(db: Session):
    return db.query(MCPServer).all()

# 更新
def update_mcp_server_db(db: Session, mcp_server_id: int, mcp_server_update: MCPServerUpdate):
    mcp_server = get_mcp_server_by_id_db(db, mcp_server_id)
    if mcp_server:
        mcp_server.desc = mcp_server_update.desc
        mcp_server.cfg = mcp_server_update.cfg
        mcp_server.protocol = mcp_server_update.protocol
        db.commit()
        db.refresh(mcp_server)
        return mcp_server
    return mcp_server

# 删除
def delete_mcp_server_db(db: Session, mcp_server_id: int):
    mcp_server = get_mcp_server_by_id_db(db, mcp_server_id)
    if mcp_server:
        db.delete(mcp_server)
        db.commit()
        return mcp_server
    return mcp_server

def toggle_mcp_server_db(db: Session, mcp_server_id: int):
    mcp_server = get_mcp_server_by_id_db(db, mcp_server_id)
    if mcp_server:
        mcp_server.is_enabled = not mcp_server.is_enabled
        db.commit()
        db.refresh(mcp_server)
        return mcp_server
    return mcp_server

def get_mcp_agent_db(db: Session, name: str):
    return db.query(MCPAgent).filter(MCPAgent.name == name).first()

def create_mcp_agent_db(db: Session, mcp_agent_create: MCPAgentCreate):
    mcp_agent = MCPAgent(**mcp_agent_create.model_dump())
    db.add(mcp_agent)
    db.commit()
    db.refresh(mcp_agent)
    return mcp_agent

def get_mcp_agent_by_id_db(db: Session, mcp_agent_id: int):
    return db.query(MCPAgent).filter(MCPAgent.id == mcp_agent_id).first()

def get_mcp_agent_list_db(db: Session):
    return db.query(MCPAgent).all()

def update_mcp_agent_db(db: Session, mcp_agent_id: int, mcp_agent_update: MCPAgentUpdate):
    mcp_agent = get_mcp_agent_by_id_db(db, mcp_agent_id)
    if mcp_agent:
        for field, value in mcp_agent_update.model_dump(exclude_unset=True).items():
            setattr(mcp_agent, field, value)
        db.commit()
        db.refresh(mcp_agent)
        return mcp_agent
    return mcp_agent

def delete_mcp_agent_db(db: Session, mcp_agent_id: int):
    mcp_agent = get_mcp_agent_by_id_db(db, mcp_agent_id)
    if mcp_agent:
        db.delete(mcp_agent)
        db.commit()
        return mcp_agent
    return mcp_agent