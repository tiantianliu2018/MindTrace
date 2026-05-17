from __future__ import annotations

from unittest.mock import patch


class TestCreateDiary:
    def test_create_diary_success(self, client, db_session):
        mock_result = {
            "emotion": "anxious",
            "intensity": 0.65,
            "themes": ["工作压力", "调试"],
            "insight": "任务驱动型焦虑，完成后有所缓解。",
        }
        with patch("app.service.diary_service.analyze_text", return_value=mock_result):
            response = client.post(
                "/api/diary",
                json={"date": "2026-05-16", "content": "今天调bug很烦，但最后跑通了。"},
            )

        assert response.status_code == 200
        data = response.json()
        assert data["emotion"] == "anxious"
        assert data["intensity"] == 0.65
        assert data["themes"] == ["工作压力", "调试"]
        assert data["insight"] == "任务驱动型焦虑，完成后有所缓解。"
        assert data["emotion_group"] == "negative"
        assert data["emotion_valence"] == "unpleasant"
        assert data["emotion_energy"] == "high"
        assert data["id"] is not None
        assert data["date"] == "2026-05-16"

    def test_create_diary_empty_content(self, client):
        response = client.post(
            "/api/diary",
            json={"date": "2026-05-16", "content": ""},
        )
        assert response.status_code == 422

    def test_create_diary_future_date(self, client):
        response = client.post(
            "/api/diary",
            json={"date": "2099-01-01", "content": "测试未来日期。"},
        )
        assert response.status_code == 422

    def test_create_diary_content_too_long(self, client):
        response = client.post(
            "/api/diary",
            json={"date": "2026-05-16", "content": "长" * 5001},
        )
        assert response.status_code == 422


class TestGetDiaries:
    def test_list_empty(self, client):
        response = client.get("/api/diary?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert data["items"] == []

    def test_list_with_entries(self, client):
        mock_result = {
            "emotion": "calm",
            "intensity": 0.3,
            "themes": ["阅读"],
            "insight": "安静的阅读时光。",
        }
        with patch("app.service.diary_service.analyze_text", return_value=mock_result):
            client.post("/api/diary", json={"date": "2026-05-15", "content": "今天看书很平静。"})
            client.post("/api/diary", json={"date": "2026-05-16", "content": "今天继续看书。"})

        response = client.get("/api/diary?limit=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 2
        assert data["items"][0]["date"] == "2026-05-16"
        assert data["items"][1]["date"] == "2026-05-15"

    def test_list_respects_limit(self, client):
        mock_result = {
            "emotion": "calm",
            "intensity": 0.3,
            "themes": ["阅读"],
            "insight": "安静的阅读时光。",
        }
        with patch("app.service.diary_service.analyze_text", return_value=mock_result):
            for i in range(5):
                client.post("/api/diary", json={"date": f"2026-05-{10 + i:02d}", "content": f"日记内容{i}。"})

        response = client.get("/api/diary?limit=2")
        data = response.json()
        assert len(data["items"]) == 2


class TestGetSummary:
    def test_summary_empty_range(self, client):
        response = client.get("/api/diary/summary?start_date=2026-05-01&end_date=2026-05-10")
        assert response.status_code == 200
        data = response.json()
        assert data["total_entries"] == 0
        assert data["average_intensity"] == 0.0

    def test_summary_period_week(self, client):
        mock_analyze = {
            "emotion": "anxious",
            "intensity": 0.5,
            "themes": ["工作"],
            "insight": "测试洞察。",
        }
        mock_summary = {
            "summary": "本周情绪波动较大。",
            "trend": "呈上升趋势。",
            "highlights": ["完成任务", "坚持记录"],
            "suggestion": "继续保持记录习惯。",
        }
        with (
            patch("app.service.diary_service.analyze_text", return_value=mock_analyze),
            patch("app.service.diary_service.summarize_diaries", return_value=mock_summary),
        ):
            client.post("/api/diary", json={"date": "2026-05-15", "content": "测试日记。"})

        with patch("app.service.diary_service.summarize_diaries", return_value=mock_summary):
            response = client.get("/api/diary/summary?period=week&anchor_date=2026-05-16")

        assert response.status_code == 200
        data = response.json()
        assert data["total_entries"] > 0
        assert data["summary"] == "本周情绪波动较大。"
        assert data["trend"] == "呈上升趋势。"
        assert "完成任务" in data["highlights"]

    def test_summary_missing_params(self, client):
        response = client.get("/api/diary/summary")
        assert response.status_code == 400
