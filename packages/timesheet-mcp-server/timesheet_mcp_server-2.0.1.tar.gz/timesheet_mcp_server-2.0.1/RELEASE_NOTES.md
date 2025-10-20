# 工时管理系统 MCP 服务器 - 正式版本

## 版本信息

- **版本号**: 2.0.0
- **发布日期**: 2025-10-20
- **框架**: FastMCP 2.0
- **协议**: MCP (Model Context Protocol)

## 功能特性

### 核心功能

1. **工时记录查询** (`get_my_time_entries`)
   - 查询当前用户的工时记录
   - 支持按项目、时间范围、审批状态过滤
   - 分页查询，灵活控制数据量

2. **项目信息查询** (`get_projects`)
   - 查询系统中的项目列表
   - 支持按状态、业务线过滤
   - 获取项目详细信息

3. **健康检查** (`health_check`)
   - 验证 MCP 服务器运行状态
   - 检查 API 连接和认证
   - 故障诊断和监控

### 技术特性

- ✅ **异步架构**: 基于 asyncio 的高性能异步处理
- ✅ **错误处理**: 完善的异常捕获和错误提示
- ✅ **重试机制**: 自动重试失败的请求（最多3次，指数退避）
- ✅ **类型安全**: 使用 Pydantic 进行数据验证
- ✅ **日志记录**: 详细的运行日志，便于调试
- ✅ **环境配置**: 灵活的环境变量配置

## 安装和配置

### 系统要求

- Python 3.10+
- uvx 或 uv 包管理器
- 有效的工时管理系统 API 访问权限

### 快速开始

1. **克隆项目**
```bash
git clone <repository-url>
cd timesheet-mcp-server-v2
```

2. **配置环境变量**
```bash
cp .env.example .env
# 编辑 .env 文件，设置 API URL 和 Token
```

3. **在 Cursor 中配置**

编辑 `.cursor/mcp.json`:
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
        "TIMESHEET_API_TOKEN": "your-jwt-token-here"
      }
    }
  }
}
```

4. **重启 Cursor**

重启后即可在 Tools & MCP 中看到 timesheet-mcp 服务器。

## 使用文档

### 工具说明

#### 1. health_check

检查服务器和 API 连接状态。

**使用场景**:
- 初次配置后验证连接
- 排查 Token 过期问题
- 监控服务器运行状态

**示例**:
```
请检查 MCP 服务器状态
```

#### 2. get_my_time_entries

查询当前用户的工时记录。

**参数**:
- `page`: 页码（默认 1）
- `limit`: 每页记录数（默认 10）
- `project_id`: 项目ID过滤
- `start_date`: 开始日期（YYYY-MM-DD）
- `end_date`: 结束日期（YYYY-MM-DD）
- `status`: 状态（submitted/approved/rejected）

**示例**:
```
查询我最近20条工时记录
查询我在项目123的工时记录
查询我2025年1月的工时记录
查询我待审批的工时记录
```

#### 3. get_projects

查询项目列表。

**参数**:
- `page`: 页码（默认 1）
- `limit`: 每页记录数（默认 10）
- `status`: 项目状态
- `business_line_id`: 业务线ID

**示例**:
```
查询所有项目
查询业务线8的项目
查询进行中的项目
```

## 架构设计

### 目录结构

```
timesheet-mcp-server-v2/
├── src/
│   ├── server.py          # MCP 服务器主文件
│   ├── client.py          # HTTP 客户端
│   ├── models.py          # 数据模型
│   └── tools/             # 工具模块（预留）
├── config/
│   └── settings.py        # 配置管理
├── .env                   # 环境变量
├── requirements.txt       # Python 依赖
└── README.md             # 项目文档
```

### 核心组件

1. **FastMCP 服务器** (`src/server.py`)
   - 工具注册和管理
   - 请求处理和响应
   - 错误处理

2. **HTTP 客户端** (`src/client.py`)
   - 异步 HTTP 请求
   - 自动重试机制
   - 错误分类处理

3. **配置管理** (`config/settings.py`)
   - 环境变量加载
   - 配置验证
   - 默认值设置

## 维护和更新

### JWT Token 更新

Token 有效期为 7 天，过期后需要重新生成：

```bash
cd backend
go run cmd/generate_jwt/main.go -username=<your-username>
```

然后更新 MCP 配置中的 `TIMESHEET_API_TOKEN`。

### 日志调试

修改 `.env` 中的日志级别：

```env
MCP_LOG_LEVEL=DEBUG  # 可选: DEBUG, INFO, WARNING, ERROR
```

### 常见问题

1. **Token 过期**
   - 错误: "认证失败：Token 可能已过期"
   - 解决: 重新生成 Token 并更新配置

2. **API 连接失败**
   - 错误: "服务器错误：HTTP 502"
   - 解决: 检查 API 地址和网络连接

3. **工具不显示**
   - 解决: 检查配置文件路径，重启 Cursor

## 技术支持

- **项目地址**: https://github.com/yangyuezheng/ai-emp
- **文档**: 查看项目 docs/ 目录
- **问题反馈**: 提交 GitHub Issue

## 许可证

MIT License

---

**配置完成时间**: 2025-10-20  
**状态**: ✅ 生产就绪

