# ragflow-mcp-server-aider MCP server

RAGFlow MCP Server Aider

## Components



### Tools
  
### Tools
  
1. list_datasets
    - 列出所有数据集
    - 返回数据集的 ID 和名称

2. create_chat
    - 创建一个新的聊天助手
    - 输入：
      - name: 聊天助手的名称
      - dataset_id: 数据集的 ID
    - 返回创建的聊天助手的 ID、名称和会话 ID

3. chat
    - 与聊天助手进行对话
    - 输入：
      - session_id: 聊天助手的会话 ID
      - question: 提问内容
    - 返回聊天助手的回答
4. retrieve
   - 检索相关信息
    - 输入：
      - dataset_ids: 数据集的 ID
      - question: 提问内容
    - 返回从知识库检索到的内容

## Configuration

[TODO: Add configuration details specific to your implementation]

## Quickstart

### Install

#### Claude Desktop

On MacOS: `~/Library/Application\ Support/Claude/claude_desktop_config.json`
On Windows: `%APPDATA%/Claude/claude_desktop_config.json`

<details>
  <summary>Development/Unpublished Servers Configuration</summary>
  ```
  "mcpServers": {
    "ragflow-mcp-server-aider": {
      "command": "uv",
      "args": [
        "--directory",
        ".\path\to\ragflow-mcp-server-aider",
        "run",
        "ragflow-mcp-server-aider"
      ]
    }
  }
  ```
</details>

<details>
  <summary>Published Servers Configuration</summary>
  ```
  "mcpServers": {
    "ragflow-mcp-server-aider": {
      "command": "uvx",
      "args": [
        "ragflow-mcp-server-aider"
      ]
    }
  }
  ```
</details>

## Development

### Building and Publishing

To prepare the package for distribution:

1. Sync dependencies and update lockfile:
```bash
uv sync
```

2. Build package distributions:
```bash
uv build
```

This will create source and wheel distributions in the `dist/` directory.

3. Publish to PyPI:
```bash
uv publish
```

Note: You'll need to set PyPI credentials via environment variables or command flags:
- Token: `--token` or `UV_PUBLISH_TOKEN`
- Or username/password: `--username`/`UV_PUBLISH_USERNAME` and `--password`/`UV_PUBLISH_PASSWORD`

### Debugging

Since MCP servers run over stdio, debugging can be challenging. For the best debugging
experience, we strongly recommend using the [MCP Inspector](https://github.com/modelcontextprotocol/inspector).


You can launch the MCP Inspector via [`npm`](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) with this command:

```bash
npx @modelcontextprotocol/inspector uv --directory .\path\to\ragflow-mcp-server-aider run ragflow-mcp-server-aider
```


Upon launching, the Inspector will display a URL that you can access in your browser to begin debugging.