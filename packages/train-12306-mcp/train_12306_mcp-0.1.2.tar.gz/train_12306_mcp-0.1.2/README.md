# <div align="center">train_12306_mcp</div>

12306 MCP server, implementing the ticket inquiry feature.

基于 Model Context Protocol (MCP) 的12306购票搜索服务器。

<div align="center"> 

| 功能描述                         | 状态     |
|------------------------------|--------|
| 查询12306购票信息              | ✅ 已完成  |
| 过滤列车信息                   | ✅ 已完成  |
| 过站查询                      | ✅ 已完成 |
| 中转查询                      | ✅ 已完成 |

</div>

## <div align="center">⚙️Installation</div>

## <div align="center">▶️Quick Start</div>

### CLI-stdio
~~~bash
uv run -m train_12306_mcp
~~~

### MCP sever configuration

~~~json
{
  "mcpServers": {
    "train_12306_mcp": {
      "args": [
        "train_12306_mcp@latest"
      ],
      "command": "uvx"
    }
  }
}
~~~

