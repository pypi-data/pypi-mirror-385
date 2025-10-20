# Token 管理指南

本文档介绍如何为 MCP 服务器生成和管理长期有效的 JWT Token。

## 为什么需要长期 Token？

MCP 服务器是一个长期运行的服务，频繁更换 Token 会导致：
- ❌ Token 过期后服务中断
- ❌ 需要经常手动更新配置
- ❌ 影响使用体验

**解决方案**：生成一个长期有效的 JWT Token（推荐 365 天或更长）

## 方法一：使用后端 Go 工具生成（推荐）⭐

### 1. 进入后端目录

```bash
cd backend/cmd/generate_jwt
```

### 2. 生成长期 Token

```bash
# 生成 1 年有效期的 Token
go run main.go -username=杨月政 -expiration-days=365

# 生成 3 年有效期的 Token
go run main.go -username=杨月政 -expiration-days=1095

# 生成 10 年有效期的 Token（几乎永久）
go run main.go -username=杨月政 -expiration-days=3650
```

### 3. 复制输出的 Token

工具会输出类似以下内容：

```
=== JWT Token 生成成功 ===
用户ID: 29
用户名: yangyuezheng
真实姓名: 杨月政
角色: super_admin
有效期: 365 天
过期时间: 2026-10-20 12:00:00

JWT Token:
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

=== MCP 配置示例 ===
"env": {
  "TIMESHEET_API_BASE_URL": "https://tms.ktvsky.com/api",
  "TIMESHEET_API_TOKEN": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### 4. 更新 MCP 配置

将生成的 Token 更新到以下配置文件中：

**`.mcp.json`** (Claude Desktop):
```json
{
  "mcpServers": {
    "timesheet": {
      "command": "uvx",
      "args": [
        "--from", "/path/to/timesheet-mcp-server-v2",
        "fastmcp", "run", "/path/to/timesheet-mcp-server-v2/src/server.py"
      ],
      "env": {
        "TIMESHEET_API_BASE_URL": "https://tms.ktvsky.com/api",
        "TIMESHEET_API_TOKEN": "你生成的Token"
      }
    }
  }
}
```

**`.cursor/mcp.json`** (Cursor IDE):
```json
{
  "mcpServers": {
    "timesheet-mcp": {
      "command": "uvx",
      "args": [
        "--from", "/path/to/timesheet-mcp-server-v2",
        "fastmcp", "run", "/path/to/timesheet-mcp-server-v2/src/server.py"
      ],
      "env": {
        "TIMESHEET_API_BASE_URL": "https://tms.ktvsky.com/api",
        "TIMESHEET_API_TOKEN": "你生成的Token"
      }
    }
  }
}
```

**`timesheet-mcp-server-v2/.env`**:
```env
TIMESHEET_API_BASE_URL=https://tms.ktvsky.com/api
TIMESHEET_API_TOKEN=你生成的Token
```

## 方法二：使用 Python 工具生成

### 1. 安装依赖

```bash
cd timesheet-mcp-server-v2
pip install PyJWT
```

### 2. 生成 Token

```bash
# 生成 1 年有效期的 Token
python tools/generate_token.py --user-id 29 --username "杨月政" --days 365

# 生成 3 年有效期的 Token
python tools/generate_token.py --user-id 29 --username "杨月政" --days 1095

# 直接输出 .env 格式
python tools/generate_token.py --user-id 29 --username "杨月政" --days 365 --output env

# 直接输出 MCP 配置格式
python tools/generate_token.py --user-id 29 --username "杨月政" --days 365 --output config
```

## 常见问题

### Q: Token 应该设置多长有效期？

**A**: 建议根据使用场景：
- 个人开发环境：365 天（1年）或更长
- 团队共享环境：90-180 天
- 生产环境：根据安全策略决定

### Q: Token 过期后怎么办？

**A**: 重新生成一个新的 Token，并更新配置文件，然后重启 MCP 服务器。

### Q: 如何验证 Token 是否有效？

**A**: 使用健康检查工具：
```bash
# 在 Cursor/Claude 中运行
mcp_timesheet-mcp_health_check
```

或使用 curl 测试：
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://tms.ktvsky.com/api/time-entries/my?limit=1
```

### Q: 不同用户的 Token 有什么区别？

**A**: Token 绑定了用户身份和角色：
- `super_admin`: 超级管理员，拥有所有权限
- `manager`: 管理员，可管理项目和人员
- `project_member`: 普通成员，只能查看和管理自己的工时

确保使用正确用户的 Token，否则可能无法访问某些数据。

### Q: Token 泄露了怎么办？

**A**: 立即重新生成新的 Token 并更新配置。由于 Token 有过期时间，旧的 Token 会在过期后自动失效。

## 安全建议

1. ✅ **不要将 Token 提交到版本控制系统**
   - 将 `.env`、`.mcp.json` 等文件添加到 `.gitignore`
   
2. ✅ **定期更换 Token**
   - 即使使用长期 Token，也建议定期（如每年）更换一次

3. ✅ **为不同环境使用不同的 Token**
   - 开发环境、测试环境、生产环境使用不同的 Token

4. ✅ **限制 Token 权限**
   - 普通使用场景使用 `project_member` 角色即可
   - 只在必要时使用 `super_admin` 角色

## 快速参考

```bash
# Go 工具 - 生成 1 年期 Token
cd backend/cmd/generate_jwt
go run main.go -username=杨月政 -expiration-days=365

# Python 工具 - 生成 1 年期 Token
cd timesheet-mcp-server-v2
python tools/generate_token.py --user-id 29 --username "杨月政" --days 365 --output config
```

复制生成的 Token 到 `.mcp.json` 和 `.cursor/mcp.json`，重启 MCP 服务器即可。

