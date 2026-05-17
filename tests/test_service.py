from __future__ import annotations

from datetime import date

import pytest

from app.service.ai_service import (
    _build_context_text,
    _build_prompt,
    _default_response,
    _parse_response_text,
    normalize_emotion_label,
    get_emotion_metadata,
    SUGGESTED_THEMES,
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
        assert "emotions" in prompt
        assert "intensity" in prompt
        assert "themes" in prompt
        assert "insight" in prompt
        assert "trigger" in prompt
        assert "physical_state" in prompt

    def test_prompt_includes_suggested_themes(self):
        prompt = _build_prompt("测试内容。")
        for theme in SUGGESTED_THEMES[:3]:
            assert theme in prompt

    def test_prompt_includes_context(self):
        context = _build_context_text([
            {"date": "2026-05-15", "emotion": "calm", "themes": ["阅读"], "content": "今天看书很平静。"},
        ])
        prompt = _build_prompt("今天继续看书。", context)
        assert "2026-05-15" in prompt
        assert "calm" in prompt
        assert "阅读" in prompt


class TestBuildContextText:
    def test_empty_context(self):
        assert _build_context_text(None) == ""
        assert _build_context_text([]) == ""

    def test_with_entries(self):
        context = _build_context_text([
            {"date": "2026-05-15", "emotion": "calm", "themes": ["阅读"], "content": "今天看书很平静。"},
        ])
        assert "2026-05-15" in context
        assert "calm" in context
        assert "阅读" in context
        assert "今天看书很平静" in context


class TestParseResponseText:
    def test_parse_with_compound_emotions(self):
        result = _parse_response_text(
            '{"emotions": [{"emotion": "anxious", "proportion": 0.6}, {"emotion": "hopeful", "proportion": 0.4}], '
            '"intensity": 0.65, "themes": ["工作", "压力"], "insight": "混合情绪。", '
            '"trigger": "项目延期", "physical_state": "疲劳"}'
        )
        assert result["emotion"] == "anxious"
        assert len(result["emotions"]) == 2
        assert result["emotions"][0] == {"emotion": "anxious", "proportion": 0.6}
        assert result["intensity"] == 0.65
        assert result["trigger"] == "项目延期"
        assert result["physical_state"] == "疲劳"

    def test_parse_normalizes_proportions(self):
        result = _parse_response_text(
            '{"emotions": [{"emotion": "joyful", "proportion": 2.0}, {"emotion": "calm", "proportion": 2.0}], '
            '"intensity": 0.5, "themes": [], "insight": "test", "trigger": "", "physical_state": ""}'
        )
        assert result["emotions"][0]["proportion"] == 0.5
        assert result["emotions"][1]["proportion"] == 0.5

    def test_parse_with_code_block(self):
        result = _parse_response_text(
            '```json\n{"emotions": [{"emotion": "calm", "proportion": 1.0}], "intensity": 0.3, '
            '"themes": [], "insight": "平静的一天。", "trigger": "", "physical_state": ""}\n```'
        )
        assert result["emotion"] == "calm"
        assert result["intensity"] == 0.3

    def test_parse_backward_compat_single_emotion(self):
        result = _parse_response_text(
            '{"emotion": "joyful", "intensity": 0.8, '
            '"themes": ["生活"], "insight": "积极的反馈。", "trigger": "", "physical_state": ""}'
        )
        assert result["emotion"] == "joyful"
        assert len(result["emotions"]) == 1

    def test_parse_invalid_json(self):
        with pytest.raises(Exception):
            _parse_response_text("not valid json")


class TestDefaultResponse:
    def test_default_response_includes_new_fields(self):
        result = _default_response("测试错误")
        assert result["emotion"] == "unknown"
        assert result["emotions"] == [{"emotion": "unknown", "proportion": 1.0}]
        assert result["trigger"] == ""
        assert result["physical_state"] == ""
        assert result["compared_to_previous"] == ""


class TestResolveSummaryRange:
    def test_custom_range(self):
        start, end = resolve_summary_range(
            period=None, anchor_date=None,
            start_date=date(2026, 5, 1), end_date=date(2026, 5, 10),
        )
        assert start == date(2026, 5, 1)
        assert end == date(2026, 5, 10)

    def test_period_week(self):
        start, end = resolve_summary_range(
            period="week", anchor_date=date(2026, 5, 13),
            start_date=None, end_date=None,
        )
        assert (end - start).days == 6

    def test_period_month(self):
        start, end = resolve_summary_range(
            period="month", anchor_date=date(2026, 5, 15),
            start_date=None, end_date=None,
        )
        assert start.month == 5
        assert start.day == 1
        assert end.month == 5

    def test_missing_params_raises(self):
        with pytest.raises(ValueError, match="请提供"):
            resolve_summary_range(period=None, anchor_date=None, start_date=None, end_date=None)
