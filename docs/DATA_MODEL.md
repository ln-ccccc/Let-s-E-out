# 数据模型（DATA_MODEL）｜探店复盘 App（暂定名）

目标：用最少的实体覆盖 MVP（记录/公开/收藏/举报/反馈），并为后续“圈子协作”预留扩展点。

> 说明：字段类型用 Postgres 语义描述；其他数据库可按等价类型映射。

## 1. 实体关系概览

- `users` 1—N `visits`（一个用户可写多条复盘）
- `places` 1—N `visits`（一个店铺可对应多次到店复盘）
- `users` N—N `visits` via `favorites`（用户收藏公开复盘）
- `users` 1—N `reports`（用户可举报多条内容）
- `users` 1—N `feedbacks`（用户可提交多条反馈）

## 2. 枚举与约定

### 2.1 publish_status（公开状态）
- `private`：仅作者可见
- `public`：所有人可见（进入公开页、可被收藏/举报）
- `unlisted`（可选）：通过链接可见，不进入公开列表（V1 可加）

### 2.2 revisit_intent（会不会再去）
- `yes` / `maybe` / `no`

### 2.3 day_part（到店时段）
- `breakfast` / `lunch` / `dinner` / `late_night` / `other`

### 2.4 report_reason（举报原因）
- `abuse`（辱骂/攻击）
- `defamation`（诽谤/造谣/商家纠纷）
- `porn`（色情低俗）
- `privacy`（隐私泄露）
- `other`

### 2.5 feedback_type（反馈类型）
- `bug` / `suggestion` / `content` / `other`

### 2.6 spice_tolerance（辣度偏好）
建议用整数表达（便于筛选/统计）：
- `0`：不能吃辣
- `1`：微辣
- `2`：中辣
- `3`：重辣

### 2.7 flavor_preference（口味偏好）
- `light`（清淡）/ `normal`（正常）/ `heavy`（重口）

### 2.8 taste_profile_visibility（口味偏好展示范围）
MVP 先支持两档：
- `public`：展示在公开内容中
- `private`：仅自己可见（不对外展示）

## 3. 表设计（MVP）

### 3.1 users
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | uuid | PK | 用户 id |
| created_at | timestamptz | not null | 创建时间 |
| nickname | text | not null | 昵称（可随机生成） |
| avatar_url | text | null | 头像 |
| home_province | text | null | 来自哪里（省/州，可选） |
| home_city | text | null | 来自哪里（市/县，可选） |
| spice_tolerance | smallint | null | 辣度偏好：0-3（见 2.6） |
| flavor_preference | text | null | 口味偏好：light/normal/heavy |
| taste_profile_visibility | text | not null default 'public' | 口味偏好展示范围 |
| role | text | not null default 'user' | `user` / `admin` |
| status | text | not null default 'active' | `active` / `banned` |

索引建议：
- `(created_at)`
- `(role, status)`

### 3.2 places（店铺）
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | uuid | PK | 店铺 id |
| created_at | timestamptz | not null | 创建时间 |
| created_by | uuid | FK users(id) | 首次创建人 |
| name | text | not null | 店名 |
| city | text | not null | 城市（如 武汉） |
| area | text | null | 区域/商圈（MVP 文本即可） |
| address | text | null | 详细地址（可选） |
| category | text | null | 品类（火锅/日料等） |
| lat | double precision | null | 纬度（V1 可接 POI） |
| lng | double precision | null | 经度（V1 可接 POI） |
| source | text | not null default 'user' | `user` / `poi`（V1） |

约束建议：
- 同城同名不强制唯一（现实存在重名），可先不做去重；后续做合并机制。

索引建议：
- `(city, name)`
- `(city, area)`

### 3.3 visits（探店复盘）
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | uuid | PK | 复盘 id |
| created_at | timestamptz | not null | 创建时间 |
| updated_at | timestamptz | not null | 更新时间 |
| author_id | uuid | FK users(id) not null | 作者 |
| place_id | uuid | FK places(id) not null | 店铺 |
| visited_on | date | null | 到店日期（可选） |
| day_part | text | not null | 时段枚举 |
| publish_status | text | not null default 'private' | 公开状态 |
| rating | smallint | null | 评分（1-5，可选） |
| price_per_person | integer | null | 人均（元，可选） |
| queue_minutes | integer | null | 等位分钟 |
| highlights | text | not null | 推荐点（必填） |
| pitfalls | text | not null | 踩坑点（必填） |
| revisit_intent | text | not null | 会不会再去 |
| recommended_items | text[] | null | 推荐菜（数组） |
| avoid_items | text[] | null | 雷菜（数组） |
| scenarios | text[] | null | 适合场景（数组枚举） |
| tags | text[] | null | 标签（数组） |
| photo_urls | text[] | null | 图片 url（数组） |
| is_deleted | boolean | not null default false | 软删除 |

约束建议：
- `highlights`、`pitfalls`、`revisit_intent`、`day_part` 非空
- `queue_minutes >= 0`，`price_per_person >= 0`

索引建议（按查询习惯）：
- `(author_id, created_at desc)`
- `(publish_status, created_at desc)`（公开流）
- `(place_id, created_at desc)`
- GIN：`tags`, `scenarios`（若使用 Postgres 数组筛选）

### 3.4 favorites（收藏）
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| user_id | uuid | FK users(id) | 收藏者 |
| visit_id | uuid | FK visits(id) | 被收藏复盘 |
| created_at | timestamptz | not null | 收藏时间 |

约束：
- PK：`(user_id, visit_id)`（防重复）

索引建议：
- `(user_id, created_at desc)`
- `(visit_id)`

### 3.5 reports（举报）
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | uuid | PK | 举报 id |
| created_at | timestamptz | not null | 创建时间 |
| reporter_id | uuid | FK users(id) not null | 举报人 |
| target_type | text | not null | MVP：固定 `visit` |
| target_id | uuid | not null | 目标 id（visit_id） |
| reason | text | not null | 举报原因枚举 |
| description | text | null | 补充说明 |
| status | text | not null default 'open' | `open`/`triaged`/`resolved`/`rejected` |
| handled_by | uuid | FK users(id) null | 处理人（管理员） |
| handled_at | timestamptz | null | 处理时间 |
| resolution | text | null | 处理结果说明（内部） |

索引建议：
- `(status, created_at desc)`
- `(target_type, target_id)`

### 3.6 feedbacks（体验反馈）
| 字段 | 类型 | 约束 | 说明 |
|---|---|---|---|
| id | uuid | PK | 反馈 id |
| created_at | timestamptz | not null | 创建时间 |
| user_id | uuid | FK users(id) null | 未登录也可反馈则允许 null（可选策略） |
| type | text | not null | 反馈类型枚举 |
| message | text | not null | 反馈内容 |
| screenshot_urls | text[] | null | 截图 |
| contact | text | null | 联系方式（可选） |
| app_version | text | null | App 版本 |
| os | text | null | iOS/Android |
| device | text | null | 机型 |
| status | text | not null default 'received' | `received`/`in_progress`/`done` |
| handled_by | uuid | FK users(id) null | 处理人 |
| handled_at | timestamptz | null | 处理时间 |
| reply | text | null | 给用户的回复（可选） |

索引建议：
- `(status, created_at desc)`

## 4. 扩展点（V1：圈子协作，可选）

若做“朋友一起记录/共享”，可增加：

- `groups`（圈子）
- `group_members`（圈子成员与角色）
- `group_places` / `group_visits`（圈子内共享范围）
- `visit_edits`（编辑历史/版本记录，轻量审计）
