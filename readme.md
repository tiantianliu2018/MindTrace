## MindTrace

MindTrace 是一个用于记录日记、分析情绪，并逐步生成阶段性总结的 AI 应用。

当前版本已经具备：
- 提交一篇日记内容
- 调用 AI 分析情绪、强度、主题和洞察
- 通过 FastAPI 暴露接口

## 项目结构

```text
app/
  api/        # 路由层
  core/       # 配置读取
  schemas/    # 请求与响应模型
  service/    # 业务逻辑与 AI 调用
  main.py     # 应用入口
```

## 本地启动

1. 创建虚拟环境并安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. 配置环境变量

```bash
cp .env.example .env
```

然后在 `.env` 中填入你的 OpenAI Key：

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

3. 启动服务

```bash
uvicorn app.main:app --reload
```

4. 打开接口文档

访问 [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## 示例请求

`POST /api/diary`

```json
{
  "date": "2026-04-24",
  "content": "今天做项目时有点焦虑，但把一个接口跑通之后轻松了很多。"
}
```

## 下一步建议

- 增加数据库保存日记与分析结果
- 支持按周或按月生成总结
- 增加前端记录页面
- 增加基础测试
