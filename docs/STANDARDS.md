# 开发规范（STANDARDS）｜探店复盘 App（暂定名）

目标：让 SOLO Code 在实现时“风格一致、易 review、易扩展、便于开源”。

## 1. 工程原则

1) **先稳定 MVP 主链路**：登录 → 新建复盘 → 列表/筛选 → 公开发布/收藏 → 举报/反馈  
2) **少依赖、少魔法**：能用清晰的 DTO/Model 表达就不用复杂抽象  
3) **模块内聚**：按 feature 拆分（auth/visits/public/search/feedback）  
4) **统一错误处理**：网络、校验、权限错误必须有可预测的 UI 表现  
5) **配置与密钥不入库**：所有 key 走环境变量/安全配置

## 2. Git 工作流

### 2.1 分支策略（轻量）
- `main`：可发布分支（受保护）
- `dev`：集成分支（可选，小团队也可直接 main）
- `feat/<short>`：功能分支
- `fix/<short>`：修复分支

### 2.2 提交规范（Conventional Commits）
格式：
`type(scope): subject`

示例：
- `feat(visits): add revisit intent field`
- `fix(api): handle 401 token expiry`
- `refactor(ui): extract visit card component`

type 建议：
- `feat` `fix` `docs` `refactor` `test` `chore`

### 2.3 PR 规范
每个 PR 至少包含：
- 背景/目的
- 改动点（列表）
- 验证方式（手测路径/截图/日志）
- 影响面（数据迁移/接口变更/破坏性变更）

## 3. 代码风格与质量

### 3.1 基本要求
- 命名：业务用词统一（Place/Visit/Favorite/Report/Feedback）
- 单文件职责清晰：UI、状态、网络层分离
- 禁止在 UI 层直接写 SQL/复杂业务判断（放到 service/usecase）

### 3.2 Lint / Format
- 必须启用格式化与 lint（Flutter: `dart format` + `flutter analyze`；RN: eslint + prettier）
- CI 中强制执行

### 3.3 错误与日志
- 网络错误：统一映射为可展示的 `AppError`
- 日志分级：debug/info/warn/error（不要满屏 print）
- 敏感信息（token/手机号/邮箱）禁止写入日志

## 4. API 与模型约定

### 4.1 DTO 与 Domain 分层
- DTO：与 API 字段对齐（snake/camel 统一）
- Domain：App 内部使用的实体（可做轻量适配）
- 映射逻辑集中放置，避免散落在 UI

### 4.2 兼容性
接口变更原则：
- 优先新增字段，不破坏旧字段
- 删除字段需经过版本公告与灰度（MVP 可先不做复杂灰度，但要有意识）

## 5. UI/UX 规范（“无 AI 味、简洁”）

### 5.1 视觉基调
- 以系统原生风格为主：留白、灰阶、克制的强调色（1 个主色即可）
- 少用渐变/大阴影/夸张插画
- 字体：系统字体，字号层级清晰

### 5.2 信息层级
复盘卡片建议信息密度：
- 第一行：店名 + 区域（弱化）
- 第二行：会不会再去（标签/颜色）+ 时段
- 第三行：一句推荐点（截断）
- 角落：公开/私密状态

### 5.3 表单体验（3 分钟原则）
新建复盘：
- 必填项在首屏：店名、推荐点、踩坑点、会不会再去
- 其它字段折叠到“更多信息”
- 保存后明确回执（toast/snackbar + 回到详情）

### 5.4 反馈入口“可达性”
- 「我的」页一级入口：反馈与建议
- 关键页面（详情页）提供“内容问题/体验问题”的辅助入口

## 6. 配置管理与环境

至少区分：
- `development`
- `staging`（可选但推荐）
- `production`

配置包括：
- API Base URL
- 日志等级
- Sentry DSN（可选）
- 图片存储桶/域名

## 7. 安全与隐私（开发红线）

- Token 仅存安全存储（Keychain/Keystore）
- 图片上传前可选清 EXIF（V1 可做，但要写入待办）
- 管理端接口必须二次校验（role=admin）
- 删除/下架动作必须留审计（最简：handled_by + handled_at + resolution）

