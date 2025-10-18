import httpx
# 测试创建MCP Server
host = "http://localhost:8000"
def test_create_mcp_server():
    # 发起http请求
    json_data ={"name":"test_mcp_server","desc":"test_mcp_server","cfg":"{}","protocol":"stdio"}
    headers = {"Authorization": "Bearer sk-1234"}
    response = httpx.post(f"{host}/api/mcp_server",json=json_data,headers=headers)
    # 断言请求是否成功
    print(response.status_code)
    assert response.status_code == 200
    # 断言返回的MCP Server是否创建成功
    assert response.json() is not None
    # 断言返回的MCP Server的name是否正确
    assert response.json()["name"] == "test_mcp_server"

def test_get_mcp_server():
    # 发起http请求
    headers = {"Authorization": "Bearer sk-1234"}
    response = httpx.get(f"{host}/api/mcp_server/1",headers=headers)
    # 断言请求是否成功
    print(response.status_code)
    assert response.status_code == 200
    # 断言返回的MCP Server的name是否正确
    assert response.json()["name"] == "test_mcp_server"

def test_get_mcp_server_list():
    # 发起http请求
    headers = {"Authorization": "Bearer sk-1234"}
    response = httpx.get(f"{host}/api/mcp_server",headers=headers)
    # 断言请求是否成功
    print(response.status_code)
    assert response.status_code == 200
    # 断言返回的MCP Server列表是否为空
    assert response.json() is not None
    # 断言返回的MCP Server列表的第一个MCP Server的name是否正确
    assert response.json()[0]["name"] == "test_mcp_server"

def test_update_mcp_server():
    # 发起http请求
    headers = {"Authorization": "Bearer sk-1234"}
    json_data ={"desc":"11111","cfg":"{}","protocol":"stdio"}
    response = httpx.put(f"{host}/api/mcp_server/1",json=json_data,headers=headers)
    # 断言请求是否成功
    print(response.status_code)
    assert response.status_code == 200
    # 断言返回的MCP Server的desc是否正确
    assert response.json()["desc"] == "11111"

def test_delete_mcp_server():
    # 发起http请求
    headers = {"Authorization": "Bearer sk-1234"}
    response = httpx.delete(f"{host}/api/mcp_server/1",headers=headers)
    # 断言请求是否成功
    print(response.status_code)
    assert response.status_code == 200
    # 查询MCP Server列表，为空
    response = httpx.get(f"{host}/api/mcp_server",headers=headers)
    assert len(response.json()) == 0

def test_toggle_mcp_server():
    headers = {"Authorization": "Bearer sk-1234"}
    # 创建MCP Server
    json_data ={"name":"test_mcp_server","desc":"test_mcp_server","cfg":"{}","protocol":"stdio"}
    response = httpx.post(f"{host}/api/mcp_server",json=json_data,headers=headers)
    # 断言请求是否成功
    print(response.status_code)
    assert response.status_code == 200
    response = httpx.put(f"{host}/api/mcp_server/1/toggle",headers=headers)
    # 断言请求是否成功
    print(response.status_code)
    assert response.status_code == 200
    assert response.json()["is_enabled"] == False

if __name__ == "__main__":
    # test_create_mcp_server()
    # test_get_mcp_server()
    # test_get_mcp_server_list()
    # test_update_mcp_server()
    # test_delete_mcp_server()
    test_toggle_mcp_server()