# 接口规范（API）｜探店复盘 App（暂定名）

目标：定义 MVP 所需的核心接口集合，便于前后端并行开发与后续开源实现。

约定：
- Base URL：`/api/v1`
- 鉴权：`Authorization: Bearer <token>`（或等价 Session 方案）
- 时间：ISO8601（UTC 或服务端统一时区策略）
- 错误格式统一：见 1.4

## 1. 通用规范

### 1.1 分页
- Query:
  - `limit`（默认 20，最大 100）
  - `cursor`（可选，游标分页）
- Response:
  - `items: []`
  - `nextCursor: string | null`

### 1.2 资源 ID
所有资源 id 使用 `uuid` 字符串。

### 1.3 公开状态
`publish_status`: `private | public`

### 1.4 错误响应（统一）
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "highlights is required",
    "details": {
      "field": "highlights"
    }
  }
}
```

常见错误码：
- `UNAUTHORIZED`
- `FORBIDDEN`
- `NOT_FOUND`
- `VALIDATION_ERROR`
- `RATE_LIMITED`
- `INTERNAL_ERROR`

## 2. Auth（鉴权）

> 具体登录方式可替换（手机号验证码/邮箱魔法链接/OAuth）。API 仅约定“拿到 token 后怎么用”。

### 2.1 获取当前用户
`GET /me`

Response 200:
```json
{
  "id": "uuid",
  "nickname": "string",
  "avatarUrl": "string|null",
  "tasteProfile": {
    "homeProvince": "string|null",
    "homeCity": "string|null",
    "spiceTolerance": 2,
    "flavorPreference": "heavy",
    "visibility": "public"
  },
  "role": "user|admin"
}
```

### 2.2 更新个人资料（含口味偏好）
`PATCH /me`

Request（全部可选，按需更新）：
```json
{
  "nickname": "string",
  "avatarUrl": "string|null",
  "tasteProfile": {
    "homeProvince": "string|null",
    "homeCity": "string|null",
    "spiceTolerance": 2,
    "flavorPreference": "heavy",
    "visibility": "public"
  }
}
```

Response 200：同 `GET /me`

## 3. Places（店铺）

### 3.1 搜索店铺（用于新建复盘时选择）
`GET /places/search?q=xxx&city=武汉&limit=20`

Response 200:
```json
{
  "items": [
    {
      "id": "uuid",
      "name": "string",
      "city": "武汉",
      "area": "洪山区",
      "address": "string|null",
      "category": "string|null"
    }
  ],
  "nextCursor": null
}
```

### 3.2 创建店铺（MVP：允许用户手动创建）
`POST /places`

Request:
```json
{
  "name": "string",
  "city": "武汉",
  "area": "string|null",
  "address": "string|null",
  "category": "string|null"
}
```

Response 201: place object（同 3.1 item）

## 4. Visits（探店复盘）

### 4.1 创建复盘
`POST /visits`

Request:
```json
{
  "placeId": "uuid",
  "visitedOn": "2026-04-15",
  "dayPart": "lunch",
  "publishStatus": "private",
  "rating": 5,
  "pricePerPerson": 80,
  "queueMinutes": 20,
  "highlights": "推荐点（必填）",
  "pitfalls": "踩坑点（必填）",
  "revisitIntent": "yes",
  "recommendedItems": ["xxx"],
  "avoidItems": ["yyy"],
  "scenarios": ["friends", "date"],
  "tags": ["便宜", "服务好"],
  "photoUrls": ["https://..."]
}
```

Response 201:
```json
{
  "id": "uuid",
  "authorId": "uuid",
  "author": {
    "id": "uuid",
    "nickname": "string",
    "avatarUrl": "string|null",
    "tasteProfile": {
      "homeProvince": "string|null",
      "homeCity": "string|null",
      "spiceTolerance": 2,
      "flavorPreference": "heavy",
      "visibility": "public"
    }
  },
  "place": { "id": "uuid", "name": "string", "city": "武汉", "area": "string|null" },
  "createdAt": "2026-04-15T12:00:00Z",
  "updatedAt": "2026-04-15T12:00:00Z",
  "visitedOn": "2026-04-15",
  "dayPart": "lunch",
  "publishStatus": "private",
  "highlights": "string",
  "pitfalls": "string",
  "revisitIntent": "yes",
  "recommendedItems": [],
  "avoidItems": [],
  "scenarios": [],
  "tags": [],
  "photoUrls": []
}
```

### 4.2 更新复盘
`PATCH /visits/{visitId}`

规则：
- 仅作者可修改
- 公开状态变更也走此接口（或单独一个 publish 接口，二选一）

### 4.3 删除复盘（软删除）
`DELETE /visits/{visitId}`

Response 204

### 4.4 我的复盘列表
`GET /visits/mine?limit=20&cursor=...&q=...&filters...`

常用筛选 query（建议）：
- `q`：店名关键字（服务端做 join/或 place name 冗余）
- `city`、`area`
- `category`
- `publishStatus`
- `revisitIntent`
- `dayPart`
- `scenario`（可多次传参或逗号分隔）
- `tag`

Response 200：分页 items（结构同 4.1 response）

### 4.5 复盘详情
`GET /visits/{visitId}`

规则：
- `private`：仅作者可访问
- `public`：任何登录用户可访问（也可开放匿名，后续决定）

## 5. Public（公开浏览）

### 5.1 公开复盘列表（最新/可筛选）
`GET /public/visits?limit=20&cursor=...&city=武汉&area=...&category=...`

Response 200：分页 items（结构同 4.1 response）

## 6. Favorites（收藏）

### 6.1 收藏一条公开复盘
`POST /favorites`

Request:
```json
{ "visitId": "uuid" }
```

Response 201:
```json
{ "userId": "uuid", "visitId": "uuid", "createdAt": "2026-04-15T12:00:00Z" }
```

规则：
- 仅 `public` 的 visit 可被收藏（或允许收藏私密但仅自己可见，MVP 建议只允许 public）

### 6.2 取消收藏
`DELETE /favorites/{visitId}`

Response 204

### 6.3 我的收藏列表
`GET /favorites?limit=20&cursor=...`

Response 200:
```json
{
  "items": [
    { "createdAt": "2026-04-15T12:00:00Z", "visit": { "...": "同 4.1 response" } }
  ],
  "nextCursor": null
}
```

## 7. Reports（举报）

### 7.1 举报一条公开复盘
`POST /reports`

Request:
```json
{
  "targetType": "visit",
  "targetId": "uuid",
  "reason": "abuse",
  "description": "可选补充"
}
```

Response 201:
```json
{
  "id": "uuid",
  "status": "open",
  "createdAt": "2026-04-15T12:00:00Z"
}
```

## 8. Feedbacks（体验反馈）

### 8.1 提交反馈（全局入口）
`POST /feedbacks`

Request:
```json
{
  "type": "bug",
  "message": "复现步骤...",
  "screenshotUrls": ["https://..."],
  "contact": "可选",
  "appVersion": "1.0.0",
  "os": "iOS",
  "device": "iPhone 15"
}
```

Response 201:
```json
{
  "id": "uuid",
  "status": "received",
  "createdAt": "2026-04-15T12:00:00Z"
}
```

## 9. Admin（最简管理接口，可选）

> MVP 允许直接用 BaaS 控制台替代；若自建 API，建议保留以下接口。

### 9.1 举报列表
`GET /admin/reports?status=open&limit=50`

### 9.2 处理举报
`PATCH /admin/reports/{reportId}`
Request:
```json
{ "status": "resolved", "resolution": "已下架该复盘" }
```

### 9.3 下架公开复盘
`POST /admin/visits/{visitId}/takedown`

### 9.4 封禁用户
`POST /admin/users/{userId}/ban`
