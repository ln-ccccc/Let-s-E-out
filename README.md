# 探店复盘 App（MVP）

本仓库当前包含两部分：

- 产品/技术文档：[/workspace/docs](file:///workspace/docs)
- 可运行后端（FastAPI）：[/workspace/services/api](file:///workspace/services/api)

移动端（Flutter）由于沙盒环境未内置 Flutter SDK，这里提供“模板 + 一键生成脚本”，在本地安装 Flutter 后可生成完整工程并跑起来。

## 快速开始（后端）

### 1) 启动 Postgres

```bash
docker compose up -d db
```

### 2) 配置环境变量

```bash
cp services/api/.env.example services/api/.env
```

如需修改端口/数据库地址，编辑 `services/api/.env`。

### 3) 安装依赖 & 初始化数据库

```bash
python -m venv .venv
. .venv/bin/activate
pip install -r services/api/requirements.txt
alembic -c services/api/alembic.ini upgrade head
```

### 4) 启动 API

```bash
uvicorn app.main:app --reload --port 8000 --app-dir services/api
```

- OpenAPI：`http://localhost:8000/docs`
- 健康检查：`GET http://localhost:8000/health`

## 登录（手机号验证码，开发模式）

MVP 的手机号验证码在开发模式下使用固定验证码 `000000`，避免接入短信服务。

流程：

1. `POST /api/v1/auth/request-otp`
2. `POST /api/v1/auth/verify-otp`（code=000000）
3. 拿到 `accessToken` 后，对需要鉴权的接口加 `Authorization: Bearer <token>`

## 生成 Flutter 工程（本地）

先安装 Flutter SDK，然后在仓库根目录执行：

```bash
./scripts/bootstrap_flutter.sh
```

脚本会生成 `apps/mobile/` 完整 Flutter 工程，并把模板代码写入 `lib/`。

## 文档

- 需求： [PRD.md](file:///workspace/docs/PRD.md)
- 技术： [TECH.md](file:///workspace/docs/TECH.md)
- 数据： [DATA_MODEL.md](file:///workspace/docs/DATA_MODEL.md)
- 接口： [API.md](file:///workspace/docs/API.md)
