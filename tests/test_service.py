from __future__ import annotations

from datetime import date

import pytest

from app.service.ai_service import (
    _build_prompt,
    _default_response,
    _parse_response_text,
    normalize_emotion_label,
    get_emotion_metadata,
)
from app.service.diary_service import resolve_summary_range


class TestNormalizeEmotionLabel:
    def test_known_label(self):
        assert normalize_emotion_label("anxious") == "anxious"

    def test_alias_english(self):
        assert normalize_emotion_label("happy") == "joyful"

    def test_alias_chinese(self):
        assert normalize_emotion_label("焦虑") == "anxious"

    def test_case_insensitive(self):
        assert normalize_emotion_label("ANXIOUS") == "anxious"

    def test_unknown_label(self):
        assert normalize_emotion_label("nonexistent_emotion") == "unknown"


class TestEmotionMetadata:
    def test_positive_emotion(self):
        meta = get_emotion_metadata("joyful")
        assert meta["group"] == "positive"
        assert meta["valence"] == "pleasant"
        assert meta["energy"] == "high"

    def test_negative_emotion(self):
        meta = get_emotion_metadata("sad")
        assert meta["group"] == "negative"
        assert meta["valence"] == "unpleasant"
        assert meta["energy"] == "low"

    def test_unknown_emotion(self):
        meta = get_emotion_metadata("nonexistent")
        assert meta["group"] == "unknown"
        assert meta["valence"] == "unknown"
        assert meta["energy"] == "unknown"


class TestBuildPrompt:
    def test_prompt_includes_content(self):
        prompt = _build_prompt("今天心情很好。")
        assert "今天心情很好。" in prompt
        assert "emotion" in prompt
        assert "intensity" in prompt
        assert "themes" in prompt
        assert "insight" in prompt


class TestParseResponseText:
    def test_parse_valid_json(self):
        result = _parse_response_text(
            '{"emotion": "joyful", "intensity": 0.8, "themes": ["生活", "成就"], "insight": "积极的反馈。"}'
        )
        assert result["emotion"] == "joyful"
        assert result["intensity"] == 0.8
        assert result["themes"] == ["生活", "成就"]
        assert result["insight"] == "积极的反馈。"

    def test_parse_with_code_block(self):
        result = _parse_response_text(
            '```json\n{"emotion": "calm", "intensity": 0.3, "themes": [], "insight": "平静的一天。"}\n```'
        )
        assert result["emotion"] == "calm"
        assert result["intensity"] == 0.3

    def test_parse_invalid_json(self):
        with pytest.raises(Exception):
            _parse_response_text("not valid json")


class TestDefaultResponse:
    def test_default_response(self):
        result = _default_response("测试错误信息")
        assert result["emotion"] == "unknown"
        assert result["intensity"] == 0.0
        assert result["themes"] == []
        assert result["insight"] == "测试错误信息"


class TestResolveSummaryRange:
    def test_custom_range(self):
        start, end = resolve_summary_range(
            period=None,
            anchor_date=None,
            start_date=date(2026, 5, 1),
            end_date=date(2026, 5, 10),
        )
        assert start == date(2026, 5, 1)
        assert end == date(2026, 5, 10)

    def test_period_week(self):
        start, end = resolve_summary_range(
            period="week",
            anchor_date=date(2026, 5, 13),
            start_date=None,
            end_date=None,
        )
        assert (end - start).days == 6

    def test_period_month(self):
        start, end = resolve_summary_range(
            period="month",
            anchor_date=date(2026, 5, 15),
            start_date=None,
            end_date=None,
        )
        assert start.month == 5
        assert start.day == 1
        assert end.month == 5

    def test_missing_params_raises(self):
        with pytest.raises(ValueError, match="请提供"):
            resolve_summary_range(
                period=None,
                anchor_date=None,
                start_date=None,
                end_date=None,
            )
