# QCC Web UI 一键启动 - 快速参考

## 🚀 快速命令

### 生产模式（推荐日常使用）
```bash
uvx qcc web start
```
访问：http://127.0.0.1:8080

### 开发模式（推荐开发调试）
```bash
uvx qcc web start --dev
```
访问：http://127.0.0.1:5173

### 管理命令
```bash
# 查看状态
uvx qcc web status

# 停止服务（自动清理：停止代理 + 还原配置）
uvx qcc web stop

# 保持代理运行
uvx qcc web stop --keep-proxy

# 保持配置不还原
uvx qcc web stop --keep-config

# 或按 Ctrl+C
```

## 📋 常用选项

```bash
# 指定端口
uvx qcc web start --port 9000

# 指定主机
uvx qcc web start --host 0.0.0.0

# 不自动打开浏览器
uvx qcc web start --no-browser

# 组合使用
uvx qcc web start --dev --port 9000 --no-browser
```

## 🔄 模式对比

| 特性 | 生产模式 | 开发模式 |
|-----|---------|---------|
| 命令 | `uvx qcc web start` | `uvx qcc web start --dev` |
| 端口 | 8080 | 5173 (前端) + 8080 (后端) |
| 构建 | 自动构建（首次） | 无需构建 |
| 热重载 | ❌ | ✅ 前端 + 后端 |
| 启动速度 | ~2-3s | ~5-8s |
| 适用场景 | 日常使用 | 代码开发 |

## ⚡ 开发工作流

### 全栈开发（推荐）
```bash
# 一键启动前后端
uvx qcc web start --dev

# 修改代码
# - 前端: qcc-web/src/**/*.tsx
# - 后端: fastcc/web/**/*.py

# 自动热重载，无需重启！
```

### 仅前端开发
```bash
# Terminal 1: 启动生产模式后端
uvx qcc web start

# Terminal 2: 启动前端开发
cd qcc-web && npm run dev
```

### 仅后端开发
```bash
# 使用已构建的前端 + 后端热重载
uvx qcc web start --dev
```

## 🐛 常见问题

### 端口被占用
```bash
# 查看占用进程
lsof -i :8080

# 停止进程
kill -9 <PID>

# 或使用其他端口
uvx qcc web start --port 9000
```

### 服务未启动
```bash
# 检查状态
uvx qcc web status

# 查看进程
ps aux | grep -E '(uvicorn|vite)'

# 清理 PID 文件
rm ~/.qcc/web.pid
```

### 前端无法访问
```bash
# 开发模式：访问 5173 端口
http://127.0.0.1:5173

# 生产模式：访问 8080 端口
http://127.0.0.1:8080
```

## 📊 访问地址

### 生产模式
- **Web UI**: http://127.0.0.1:8080
- **API Docs**: http://127.0.0.1:8080/api/docs

### 开发模式
- **前端**: http://127.0.0.1:5173 ⭐ 主要使用
- **后端**: http://127.0.0.1:8080
- **API Docs**: http://127.0.0.1:8080/api/docs

## 💡 提示

- ✅ 开发模式修改代码立即生效
- ✅ 生产模式首次启动会自动构建
- ✅ 按 Ctrl+C 可以优雅停止服务
- ✅ 支持 Windows/macOS/Linux

## 📚 详细文档

- [快速开始指南](docs/tasks/web-ui/快速开始.md)
- [开发模式文档](docs/tasks/web-ui-dev-mode.md)
- [功能实现说明](docs/tasks/web-ui-one-command-start.md)

---

**快速开始**: `uvx qcc web start --dev` 🚀
