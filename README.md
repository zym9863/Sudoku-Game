# Sudoku Game

一个完整的全栈数独游戏，包含 React 前端、FastAPI 后端、SQLite 持久化、单元测试和 API 接口测试。

## How to Run

在项目根目录执行：

```bash
docker compose up
```

该命令会启动前端和后端服务，并通过 Docker named volume `sudoku-data` 保存 SQLite 数据。

## Services List

| Service | Address | Description |
| --- | --- | --- |
| Frontend | http://localhost:3000 | 数独游戏界面 |
| Backend API | http://localhost:8000 | FastAPI 服务 |
| API Docs | http://localhost:8000/docs | OpenAPI 文档 |
| Health Check | http://localhost:8000/api/health | 服务健康检查 |

## Verification Method

运行完整测试：

```bash
bash run_tests.sh
```

测试内容包括：

- `unit_tests/`：数独求解、唯一解校验、题盘生成、服务层状态变更、SQLite 仓储读写。
- `API_tests/`：健康检查、创建游戏、读取游戏、恢复活跃游戏、更新格子、检查答案、提示、统计和错误响应。
- `frontend/src/**/*.test.*`：前端数独工具函数和棋盘组件渲染/交互。

API 测试覆盖所有公开接口，覆盖率为 100% 的接口面。

## Gameplay

- 首次访问会自动创建一个简单难度游戏。
- 浏览器会保存 `playerId`，后端通过 SQLite 保存当前局和统计信息。
- 支持简单、中等、困难三种难度。
- 支持填数、清除、笔记、冲突高亮、答案检查、提示、计时和完成统计。

## API Summary

| Method | Path | Purpose |
| --- | --- | --- |
| `GET` | `/api/health` | 健康检查 |
| `POST` | `/api/games` | 创建新游戏 |
| `GET` | `/api/games/active/{playerId}` | 恢复玩家活跃游戏 |
| `GET` | `/api/games/{gameId}` | 读取游戏 |
| `PATCH` | `/api/games/{gameId}/cell` | 更新数字或笔记 |
| `POST` | `/api/games/{gameId}/check` | 检查当前答案 |
| `POST` | `/api/games/{gameId}/hint` | 获取并填入提示 |
| `GET` | `/api/stats/{playerId}` | 读取玩家统计 |

