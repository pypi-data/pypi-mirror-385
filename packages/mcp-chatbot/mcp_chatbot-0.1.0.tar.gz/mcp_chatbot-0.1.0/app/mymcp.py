from mcp import ClientSession,StdioServerParameters
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.sse import sse_client
from mcp.client.stdio import stdio_client
class MCPClient:
    def __init__(self,server_params:dict,protocol:str):
        self.session:ClientSession = None
        self.server_params = server_params
        self.protocol = protocol
    
    async def connect_to_server(self):
        success = False
        try:
            if self.protocol == "stdio":
                server_params = StdioServerParameters(
                    command=self.server_params.get("command",""),
                    args=self.server_params.get("args",[]),
                    env=self.server_params.get("env",{})
                )
                self._stream_context = stdio_client(server_params)
                stream = await self._stream_context.__aenter__()
                self._session_context = ClientSession(*stream)
                self.session = await self._session_context.__aenter__()
            elif self.protocol == "sse":
                server_url = self.server_params["url"]
                headers = self.server_params.get("headers",{})
                self._stream_context = sse_client(server_url,headers=headers)
                stream = await self._stream_context.__aenter__()
                self._session_context = ClientSession(*stream)
                self.session = await self._session_context.__aenter__()
            elif self.protocol == "streamable http":
                server_url = self.server_params["url"]
                headers = self.server_params.get("headers",{})
                self._stream_context = streamablehttp_client(server_url,headers=headers)
                read_stream,write_stream,_ = await self._stream_context.__aenter__()
                self._session_context = ClientSession(read_stream,write_stream)
                self.session = await self._session_context.__aenter__()
            else:
                raise ValueError(f"Invalid protocol: {self.protocol}")
            await self.session.initialize()
            print("Initialized stdio client!")
            response = await self.session.list_tools()
            tools = response.tools
            print(f"Connected to server with tools {tools}")
            success = True
        except Exception as e:
            print(f"Failed to connect to server: {str(e)}")
            if hasattr(e, '__cause__') and e.__cause__:
                print(f"Caused by: {str(e.__cause__)}")
            if hasattr(e, '__context__') and e.__context__:
                print(f"Context: {str(e.__context__)}")
            raise
        finally:
            if not success:
                await self.cleanup()
    async def ping(self):
        response = await self.session.send_ping()
        return response
    async def call_tool(self,tool_name:str,tool_params:dict):
        response = await self.session.call_tool(tool_name,tool_params)
        return response
    async def list_tools(self):
        response = await self.session.list_tools()
        return response.tools
    async def cleanup(self):
        if hasattr(self, '_session_context') and self._session_context:
            await self._session_context.__aexit__(None,None,None)
        if hasattr(self, '_stream_context') and self._stream_context:
            await self._stream_context.__aexit__(None,None,None)
            
            