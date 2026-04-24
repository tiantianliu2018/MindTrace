# MindTrace

MindTrace 是一个面向个人情绪记录与反思的 AI 应用。  
它的目标不是简单地“给日记打标签”，而是帮助用户在持续书写中看见自己的情绪变化、压力来源和生活主题，并逐步生成更有价值的阶段性总结。

这是我的第一个 AI 项目，目前正在从一个可运行的后端原型，逐步成长为一个完整的产品。

## Why MindTrace

很多日记应用停留在“记录内容”，很多 AI 工具停留在“给出回答”。

MindTrace 想做的是把两者结合起来：
- 记录每天真实的情绪和事件
- 分析文字中的情绪强度与核心主题
- 从多篇记录中提炼长期趋势
- 帮助用户形成更清晰的自我观察

## Current Features

当前版本已经支持：
- 通过 FastAPI 提供日记分析与查询接口
- 输入一段日记内容，返回情绪、强度、主题和简短洞察
- 将日记内容和分析结果保存到 SQLite 数据库
- 按日期范围生成阶段性情绪总结
- 使用 `.env` 配置 OpenAI API 信息
- 通过 Swagger 文档快速调试接口

## Example Use Case

用户输入：

```text
今天做项目时有点焦虑，但把一个接口跑通之后轻松了很多。
```

系统返回类似结果：

```json
{
  "emotion": "anxious",
  "intensity": 0.62,
  "themes": ["项目开发", "压力", "进展反馈"],
  "insight": "这段情绪主要来自任务推进中的不确定感，而完成关键步骤后带来了明显缓解。"
}
```

## Tech Stack

- Python 3
- FastAPI
- Pydantic
- Requests
- OpenAI API
- SQLite
- SQLAlchemy

## Project Structure

```text
app/
  api/        # 路由层，定义接口
  core/       # 配置读取
  models/     # 数据模型（当前还在起步阶段）
  schemas/    # 请求与响应结构
  service/    # 业务逻辑与 AI 调用
  main.py     # 应用入口
```

## Quick Start

### 1. Clone the repository

```bash
git clone git@github.com:tiantianliu2018/MindTrace.git
cd MindTrace
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

复制示例配置：

```bash
cp .env.example .env
```

然后在 `.env` 中填写：

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
DATABASE_URL=sqlite:///./mindtrace.db
```

## Run the App

```bash
uvicorn app.main:app --reload
```

启动后访问：

- Swagger UI: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)
- ReDoc: [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)

## API Example

### Request

`POST /api/diary`

```json
{
  "date": "2026-04-24",
  "content": "今天调试接口时有些烦躁，但最后看到结果跑通时又觉得很有成就感。"
}
```

### Response

```json
{
  "emotion": "mixed",
  "intensity": 0.68,
  "themes": ["开发过程", "调试压力", "成就感"],
  "insight": "这段记录同时包含了受阻时的烦躁和问题解决后的积极反馈，说明进展本身会明显影响情绪状态。"
}
```

### History Query

`GET /api/diary?limit=10`

```json
{
  "items": [
    {
      "id": 1,
      "date": "2026-04-24",
      "emotion": "mixed",
      "intensity": 0.68,
      "themes": ["开发过程", "调试压力", "成就感"],
      "insight": "这段记录同时包含了受阻时的烦躁和问题解决后的积极反馈，说明进展本身会明显影响情绪状态。",
      "created_at": "2026-04-24T21:30:00"
    }
  ]
}
```

### Summary Query

支持两种方式：

1. 自定义日期范围

`GET /api/diary/summary?start_date=2026-04-20&end_date=2026-04-26`

2. 快捷周期模式

`GET /api/diary/summary?period=week&anchor_date=2026-04-24`

或

`GET /api/diary/summary?period=month&anchor_date=2026-04-24`

```json
{
  "start_date": "2026-04-20",
  "end_date": "2026-04-26",
  "total_entries": 5,
  "average_intensity": 0.56,
  "top_themes": ["项目推进", "压力", "成就感"],
  "dominant_emotions": ["mixed", "anxious"],
  "summary": "这一阶段的情绪整体呈现出在压力中逐步建立掌控感的特点。",
  "trend": "情绪从任务压力主导，逐渐转向更稳定和有信心的状态。",
  "highlights": ["完成关键接口联调", "数据库接入稳定", "对项目方向更清晰"],
  "suggestion": "可以继续保持连续记录，特别留意哪些具体进展最能帮助你缓解焦虑。"
}
```

## Roadmap

接下来计划逐步补齐这些能力：

- 保存日记和分析结果到数据库
- 支持按周、按月生成总结
- 增加情绪趋势可视化
- 增加前端记录页面
- 增加测试与更稳定的错误处理

## Notes

- 当前项目仍处于早期阶段，更像一个持续成长中的 MVP。
- AI 分析结果用于辅助反思，不应替代专业心理咨询或医疗建议。

## Author

Created by `tiantianliu`

如果你也对 AI、情绪记录或自我追踪产品感兴趣，欢迎关注这个项目的后续迭代。
