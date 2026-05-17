from __future__ import annotations

import json
import logging
from typing import Any

import requests

from app.core.config import get_settings

logger = logging.getLogger(__name__)


EMOTION_TAXONOMY = {
    "joyful": {"group": "positive", "valence": "pleasant", "energy": "high"},
    "excited": {"group": "positive", "valence": "pleasant", "energy": "high"},
    "hopeful": {"group": "positive", "valence": "pleasant", "energy": "medium"},
    "proud": {"group": "positive", "valence": "pleasant", "energy": "medium"},
    "grateful": {"group": "positive", "valence": "pleasant", "energy": "low"},
    "relieved": {"group": "positive", "valence": "pleasant", "energy": "low"},
    "calm": {"group": "positive", "valence": "pleasant", "energy": "low"},
    "content": {"group": "positive", "valence": "pleasant", "energy": "low"},
    "focused": {"group": "neutral", "valence": "balanced", "energy": "medium"},
    "thoughtful": {"group": "neutral", "valence": "balanced", "energy": "low"},
    "confused": {"group": "neutral", "valence": "mixed", "energy": "medium"},
    "numb": {"group": "neutral", "valence": "flat", "energy": "low"},
    "anxious": {"group": "negative", "valence": "unpleasant", "energy": "high"},
    "overwhelmed": {"group": "negative", "valence": "unpleasant", "energy": "high"},
    "frustrated": {"group": "negative", "valence": "unpleasant", "energy": "high"},
    "angry": {"group": "negative", "valence": "unpleasant", "energy": "high"},
    "sad": {"group": "negative", "valence": "unpleasant", "energy": "low"},
    "lonely": {"group": "negative", "valence": "unpleasant", "energy": "low"},
    "disappointed": {"group": "negative", "valence": "unpleasant", "energy": "low"},
    "guilty": {"group": "negative", "valence": "unpleasant", "energy": "low"},
    "mixed": {"group": "mixed", "valence": "mixed", "energy": "mixed"},
    "unknown": {"group": "unknown", "valence": "unknown", "energy": "unknown"},
}

EMOTION_ALIASES = {
    "happy": "joyful",
    "happiness": "joyful",
    "开心": "joyful",
    "愉悦": "joyful",
    "兴奋": "excited",
    "期待": "hopeful",
    "有希望": "hopeful",
    "自豪": "proud",
    "感激": "grateful",
    "感谢": "grateful",
    "释然": "relieved",
    "轻松": "relieved",
    "平静": "calm",
    "满足": "content",
    "专注": "focused",
    "思考": "thoughtful",
    "困惑": "confused",
    "麻木": "numb",
    "焦虑": "anxious",
    "不安": "anxious",
    "压力很大": "overwhelmed",
    "压垮": "overwhelmed",
    "沮丧": "frustrated",
    "烦躁": "frustrated",
    "生气": "angry",
    "伤心": "sad",
    "难过": "sad",
    "孤独": "lonely",
    "失望": "disappointed",
    "内疚": "guilty",
    "自责": "guilty",
    "后悔": "guilty",
    "复杂": "mixed",
}

SUGGESTED_THEMES = [
    "工作", "学习", "人际关系", "家庭", "健康", "睡眠", "饮食", "运动",
    "进度推进", "挫折", "成就感", "自我成长", "休闲娱乐", "经济",
    "日常琐事", "未来规划", "社会事件", "独处时光", "创意表达",
]


def normalize_emotion_label(value: str) -> str:
    normalized = value.strip().lower().replace(" ", "_").replace("-", "_")
    if normalized in EMOTION_TAXONOMY:
        return normalized
    if value.strip() in EMOTION_ALIASES:
        return EMOTION_ALIASES[value.strip()]
    return EMOTION_ALIASES.get(normalized, "unknown")


def get_emotion_metadata(label: str) -> dict[str, str]:
    return EMOTION_TAXONOMY.get(label, EMOTION_TAXONOMY["unknown"])


def _build_context_text(recent_entries: list[dict[str, Any]] | None) -> str:
    if not recent_entries:
        return ""

    lines = ["以下是用户最近的日记记录摘要，供你参考情绪变化趋势："]
    for entry in recent_entries:
        lines.append(
            f"- {entry['date']}: 情绪={entry['emotion']}, "
            f"主题={', '.join(entry['themes']) if entry['themes'] else '无'}, "
            f"原文=\"{entry['content'][:80]}\""
        )
    return "\n".join(lines)


def _build_prompt(content: str, context_text: str = "") -> str:
    context_block = ""
    if context_text:
        context_block = f"""
## 用户近期记录（纵向参考）

{context_text}

---

"""
    return f"""
你是一个理性、克制的心理分析助手。

请分析以下日记，并只返回 JSON，不要输出额外解释：
{{
  "emotions": [{{"emotion": "joyful", "proportion": 0.6}}, ...],
  "intensity": 0.0,
  "themes": ["主题1", "主题2"],
  "insight": "一句简洁的分析洞察",
  "trigger": "触发情绪变化的关键事件或情境，如无明显触发写''",
  "physical_state": "从文字推测的身体/精力状态（如：精力充沛、疲劳、平静、紧张），如无法判断写''"
}}

要求：
1. emotions 必须包含至少 1 个情绪，每个包含 emotion 和 proportion（0-1），proportion 总和应为 1。
2. emotion 标签只能从以下选择：
   joyful, excited, hopeful, proud, grateful, relieved, calm, content,
   focused, thoughtful, confused, numb,
   anxious, overwhelmed, frustrated, angry, sad, lonely, disappointed, guilty,
   mixed
3. intensity 必须是 0 到 1 之间的小数。
4. themes 使用具体、一致的标签，优先从以下集合选择（也可根据内容新增）：
   {", ".join(SUGGESTED_THEMES)}
5. insight 保持温和、具体，不夸张。{"如有近期记录上下文，请在 insight 中包含与之前的情绪对比。" if context_text else ""}
6. trigger 描述什么导致了情绪变化。
7. physical_state 仅从文字推测。

{context_block}## 当前日记

{content}
""".strip()


def _build_summary_prompt(content: str, previous_period_summary: str = "") -> str:
    comparison_block = ""
    if previous_period_summary:
        comparison_block = f"""
## 上一周期参考（用于对比）

{previous_period_summary}

---

"""
    return f"""
你是一个温和、克制、结构化的情绪回顾助手。

请根据多篇日记记录，生成一个阶段总结，并只返回 JSON：
{{
  "summary": "一段简洁的阶段总结",
  "trend": "整体情绪趋势",
  "highlights": ["亮点1", "亮点2"],
  "suggestion": "一句温和的建议"
}}

要求：
1. summary 要概括这一阶段的主要心理状态和变化。
2. trend 用一句话总结变化趋势。{"如果提供了上一周期数据，请对比说明变化方向。" if previous_period_summary else ""}
3. highlights 必须是字符串数组，提炼 2 到 4 个重点。
4. suggestion 要温和、具体，不要说教。{"结合数据中具体日期的情绪波动给出针对性建议，例如特定日期的低点模式。" if comparison_block else ""}

{comparison_block}## 当前周期记录

{content}
""".strip()


def _default_response(insight: str) -> dict[str, Any]:
    return {
        "emotion": "unknown",
        "emotions": [{"emotion": "unknown", "proportion": 1.0}],
        "intensity": 0.0,
        "themes": [],
        "insight": insight,
        "trigger": "",
        "physical_state": "",
        "compared_to_previous": "",
    }


def _default_summary_response(summary: str) -> dict[str, Any]:
    return {
        "summary": summary,
        "trend": "暂时无法判断情绪趋势。",
        "highlights": [],
        "suggestion": "可以继续记录更多内容，帮助系统形成更稳定的观察。",
    }


def _clean_json_text(text: str) -> str:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()
    return cleaned


def _parse_response_text(text: str) -> dict[str, Any]:
    data = json.loads(_clean_json_text(text))
    emotions_raw = data.get("emotions", [])
    if not emotions_raw:
        emotion = normalize_emotion_label(str(data.get("emotion", "unknown")))
        emotions = [{"emotion": emotion, "proportion": 1.0}]
    else:
        total = sum(float(item["proportion"]) for item in emotions_raw) or 1.0
        emotions = [
            {
                "emotion": normalize_emotion_label(str(item["emotion"])),
                "proportion": round(float(item["proportion"]) / total, 2),
            }
            for item in emotions_raw
        ]

    primary_emotion = emotions[0]["emotion"]
    return {
        "emotion": primary_emotion,
        "emotions": emotions,
        "intensity": float(data.get("intensity", 0.0)),
        "themes": [str(item) for item in data.get("themes", [])],
        "insight": str(data.get("insight", "暂时无法生成分析，请稍后再试。")),
        "trigger": str(data.get("trigger", "")),
        "physical_state": str(data.get("physical_state", "")),
        "compared_to_previous": str(data.get("compared_to_previous", "")),
    }


def _parse_summary_response_text(text: str) -> dict[str, Any]:
    data = json.loads(_clean_json_text(text))
    return {
        "summary": str(data.get("summary", "暂时无法生成阶段总结，请稍后再试。")),
        "trend": str(data.get("trend", "暂时无法判断情绪趋势。")),
        "highlights": [str(item) for item in data.get("highlights", [])],
        "suggestion": str(data.get("suggestion", "可以继续记录更多内容，帮助系统形成更稳定的观察。")),
    }


def analyze_text(content: str, recent_entries: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    settings = get_settings()
    if not settings.openai_api_key:
        return _default_response("未检测到 OPENAI_API_KEY，请先在 .env 中配置。")

    context_text = _build_context_text(recent_entries)
    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": settings.openai_model,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "你是一个温和、克制、结构化的心理分析助手。"},
            {"role": "user", "content": _build_prompt(content, context_text)},
        ],
    }

    try:
        response = requests.post(
            f"{settings.openai_base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=data,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        text = result["choices"][0]["message"]["content"]
        parsed = _parse_response_text(text)
        return parsed
    except (requests.RequestException, KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        logger.error("AI analysis failed: %s", exc)
        return _default_response("分析服务暂时不可用，请稍后再试。")


def summarize_diaries(content: str, previous_period_entries: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    settings = get_settings()
    if not settings.openai_api_key:
        return _default_summary_response("未检测到 OPENAI_API_KEY，请先在 .env 中配置。")

    previous_summary = ""
    if previous_period_entries:
        blocks = []
        for e in previous_period_entries:
            blocks.append(
                f"日期：{e['date']}  情绪：{e['emotion']}  强度：{e['intensity']}  "
                f"主题：{', '.join(e['themes']) if e['themes'] else '无'}"
            )
        previous_summary = "\n".join(blocks)

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": settings.openai_model,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "你是一个温和、克制、结构化的情绪回顾助手。"},
            {"role": "user", "content": _build_summary_prompt(content, previous_summary)},
        ],
    }

    try:
        response = requests.post(
            f"{settings.openai_base_url.rstrip('/')}/chat/completions",
            headers=headers,
            json=data,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()
        text = result["choices"][0]["message"]["content"]
        return _parse_summary_response_text(text)
    except (requests.RequestException, KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
        logger.error("AI summary failed: %s", exc)
        return _default_summary_response("阶段总结服务暂时不可用，请稍后再试。")
