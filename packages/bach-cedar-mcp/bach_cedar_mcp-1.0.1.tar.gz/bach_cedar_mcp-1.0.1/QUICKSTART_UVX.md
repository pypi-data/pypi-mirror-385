# 🚀 CEDAR MCP 快速启动指南

## 使用 UVX 一键启动（推荐）

```bash
uvx bach-cedar-mcp
```

## 在 Cursor/Cherry Studio 中配置

### 方式一：使用 UVX（推荐）
```json
{
  "mcpServers": {
    "cedar-mcp": {
      "command": "uvx",
      "args": ["bach-cedar-mcp"],
      "env": {
        "CEDAR_API_KEY": "<YOUR_CEDAR_API_KEY>",
        "BIOPORTAL_API_KEY": "<YOUR_BIOPORTAL_API_KEY>"
      }
    }
  }
}
```

### 方式二：使用 PIP 安装后运行
先安装：
```bash
pip install bach-cedar-mcp
```

配置：
```json
{
  "mcpServers": {
    "cedar-mcp": {
      "command": "bach-cedar-mcp",
      "env": {
        "CEDAR_API_KEY": "<YOUR_CEDAR_API_KEY>",
        "BIOPORTAL_API_KEY": "<YOUR_BIOPORTAL_API_KEY>"
      }
    }
  }
}
```

## 功能列表

- `get_template`: 从 CEDAR 仓库获取模板
- `get_instances_based_on_template`: 获取特定模板的实例，支持分页

## 获取 API 密钥

### CEDAR API Key
1. 访问 [cedar.metadatacenter.org](https://cedar.metadatacenter.org)
2. 创建账号或登录
3. 导航到: Profile → API Key
4. 复制您的 API 密钥

### BioPortal API Key
1. 访问 [bioportal.bioontology.org](https://bioportal.bioontology.org)
2. 创建账号或登录
3. 导航到: Account Settings → API Key
4. 复制您的 API 密钥

## PyPI 包地址
https://pypi.org/project/bach-cedar-mcp/

## GitHub 仓库
https://github.com/BACH-AI-Tools/cedar-mcp
