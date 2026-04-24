from __future__ import annotations

import json
from typing import Any

import requests

from app.core.config import get_settings


def _build_prompt(content: str) -> str:
    return f"""
你是一个理性、克制的心理分析助手。

请分析以下日记，并只返回 JSON，不要输出额外解释：
{{
  "emotion": "情绪类型",
  "intensity": 0.0,
  "themes": ["主题1", "主题2"],
  "insight": "一句简洁的分析洞察"
}}

要求：
1. intensity 必须是 0 到 1 之间的小数。
2. themes 必须是字符串数组。
3. insight 保持温和、具体，不夸张。

日记内容：
{content}
""".strip()


def _build_summary_prompt(content: str) -> str:
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
2. trend 用一句话总结变化趋势。
3. highlights 必须是字符串数组，提炼 2 到 4 个重点。
4. suggestion 要温和、具体，不要说教。

日记记录：
{content}
""".strip()


def _default_response(insight: str) -> dict[str, Any]:
    return {
        "emotion": "unknown",
        "intensity": 0.0,
        "themes": [],
        "insight": insight,
    }


def _default_summary_response(summary: str) -> dict[str, Any]:
    return {
        "summary": summary,
        "trend": "暂时无法判断情绪趋势。",
        "highlights": [],
        "suggestion": "可以继续记录更多内容，帮助系统形成更稳定的观察。",
    }


def _parse_response_text(text: str) -> dict[str, Any]:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

    data = json.loads(cleaned)
    return {
        "emotion": str(data.get("emotion", "unknown")),
        "intensity": float(data.get("intensity", 0.0)),
        "themes": [str(item) for item in data.get("themes", [])],
        "insight": str(data.get("insight", "暂时无法生成分析，请稍后再试。")),
    }


def _parse_summary_response_text(text: str) -> dict[str, Any]:
    cleaned = text.strip()

    if cleaned.startswith("```"):
        cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

    data = json.loads(cleaned)
    return {
        "summary": str(data.get("summary", "暂时无法生成阶段总结，请稍后再试。")),
        "trend": str(data.get("trend", "暂时无法判断情绪趋势。")),
        "highlights": [str(item) for item in data.get("highlights", [])],
        "suggestion": str(data.get("suggestion", "可以继续记录更多内容，帮助系统形成更稳定的观察。")),
    }


def analyze_text(content: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.openai_api_key:
        return _default_response("未检测到 OPENAI_API_KEY，请先在 .env 中配置。")

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": settings.openai_model,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "你是一个温和、克制、结构化的心理分析助手。"},
            {"role": "user", "content": _build_prompt(content)},
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
        return _parse_response_text(text)
    except (requests.RequestException, KeyError, ValueError, TypeError, json.JSONDecodeError):
        return _default_response("分析服务暂时不可用，请稍后再试。")


def summarize_diaries(content: str) -> dict[str, Any]:
    settings = get_settings()
    if not settings.openai_api_key:
        return _default_summary_response("未检测到 OPENAI_API_KEY，请先在 .env 中配置。")

    headers = {
        "Authorization": f"Bearer {settings.openai_api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "model": settings.openai_model,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": "你是一个温和、克制、结构化的情绪回顾助手。"},
            {"role": "user", "content": _build_summary_prompt(content)},
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
    except (requests.RequestException, KeyError, ValueError, TypeError, json.JSONDecodeError):
        return _default_summary_response("阶段总结服务暂时不可用，请稍后再试。")
