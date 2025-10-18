from sqlalchemy import Boolean, Column, Integer, String

from .database import Base


class MCPServer(Base):
    __tablename__ = "mcp_servers"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    desc = Column(String, nullable=True)
    cfg = Column(String)
    protocol = Column(String)
    is_enabled = Column(Boolean, default=True, nullable=False)

class MCPAgent(Base):
    __tablename__ = "mcp_agents"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    avatar = Column(String, nullable=True)
    desc = Column(String, nullable=True)
    system_prompt = Column(String, nullable=True)
    cfg = Column(String)
    mcp_server_ids = Column(String, nullable=True)
    model_name = Column(String, nullable=True)