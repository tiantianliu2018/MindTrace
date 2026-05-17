"use strict";
const diaryForm = document.querySelector("#diary-form");
const summaryForm = document.querySelector("#summary-form");
const diaryDateInput = document.querySelector("#diary-date");
const diaryContentInput = document.querySelector("#diary-content");
const submitButton = document.querySelector("#submit-entry");
const formMessage = document.querySelector("#form-message");
const analysisEmpty = document.querySelector("#analysis-empty");
const analysisCard = document.querySelector("#analysis-card");
const analysisDate = document.querySelector("#analysis-date");
const analysisEmotion = document.querySelector("#analysis-emotion");
const analysisIntensityText = document.querySelector("#analysis-intensity-text");
const analysisIntensityBar = document.querySelector("#analysis-intensity-bar");
const analysisThemes = document.querySelector("#analysis-themes");
const analysisInsight = document.querySelector("#analysis-insight");
const analysisMeta = document.querySelector("#analysis-meta");
const analysisEmotions = document.querySelector("#analysis-emotions");
const analysisTriggerBlock = document.querySelector("#analysis-trigger-block");
const analysisTrigger = document.querySelector("#analysis-trigger");
const analysisPhysicalBlock = document.querySelector("#analysis-physical-block");
const analysisPhysicalState = document.querySelector("#analysis-physical-state");
const analysisCompareBlock = document.querySelector("#analysis-compare-block");
const analysisCompared = document.querySelector("#analysis-compared");
const summaryMode = document.querySelector("#summary-mode");
const summaryAnchorDate = document.querySelector("#summary-anchor-date");
const summaryStartDate = document.querySelector("#summary-start-date");
const summaryEndDate = document.querySelector("#summary-end-date");
const anchorDateField = document.querySelector("#anchor-date-field");
const customRangeFields = document.querySelector("#custom-range-fields");
const summaryEmpty = document.querySelector("#summary-empty");
const summaryCard = document.querySelector("#summary-card");
const summaryRange = document.querySelector("#summary-range");
const summaryCount = document.querySelector("#summary-count");
const summaryIntensity = document.querySelector("#summary-intensity");
const summaryEmotions = document.querySelector("#summary-emotions");
const summaryText = document.querySelector("#summary-text");
const summaryTrend = document.querySelector("#summary-trend");
const summaryHighlights = document.querySelector("#summary-highlights");
const summaryThemes = document.querySelector("#summary-themes");
const summarySuggestion = document.querySelector("#summary-suggestion");
const historyList = document.querySelector("#history-list");
const entryCount = document.querySelector("#entry-count");
const topEmotion = document.querySelector("#top-emotion");
const topTheme = document.querySelector("#top-theme");
function assertElement(element, name) {
    if (!element) {
        throw new Error(`Missing required element: ${name}`);
    }
    return element;
}
function renderThemeList(container, values) {
    container.innerHTML = "";
    if (values.length === 0) {
        const chip = document.createElement("span");
        chip.className = "theme-chip";
        chip.textContent = "暂无";
        container.appendChild(chip);
        return;
    }
    values.forEach((value) => {
        const chip = document.createElement("span");
        chip.className = "theme-chip";
        chip.textContent = value;
        container.appendChild(chip);
    });
}
function formatDate(value) {
    return new Date(value).toLocaleDateString("zh-CN", {
        year: "numeric",
        month: "short",
        day: "numeric",
    });
}
function updateOverview(items) {
    assertElement(entryCount, "entry-count").textContent = String(items.length);
    assertElement(topEmotion, "top-emotion").textContent = items[0]?.emotion ?? "-";
    assertElement(topTheme, "top-theme").textContent = items[0]?.themes[0] ?? "-";
}
function renderAnalysis(item) {
    assertElement(analysisEmpty, "analysis-empty").classList.add("hidden");
    assertElement(analysisCard, "analysis-card").classList.remove("hidden");
    assertElement(analysisDate, "analysis-date").textContent = formatDate(item.date);
    assertElement(analysisEmotion, "analysis-emotion").textContent = item.emotion;
    assertElement(analysisMeta, "analysis-meta").textContent = `${item.emotion_group} / ${item.emotion_valence} / ${item.emotion_energy}`;
    assertElement(analysisIntensityText, "analysis-intensity-text").textContent = item.intensity.toFixed(2);
    assertElement(analysisIntensityBar, "analysis-intensity-bar").style.width = `${Math.max(0, Math.min(item.intensity, 1)) * 100}%`;
    const emotionsEl = assertElement(analysisEmotions, "analysis-emotions");
    emotionsEl.innerHTML = "";
    if (item.emotions && item.emotions.length > 0) {
        item.emotions.forEach((ei) => {
            const bar = document.createElement("div");
            bar.className = "emotion-bar-item";
            bar.innerHTML = `
        <div class="emotion-bar-label">${ei.emotion}</div>
        <div class="emotion-bar-track">
          <div class="emotion-bar-fill" style="width:${(ei.proportion * 100).toFixed(1)}%"></div>
        </div>
        <div class="emotion-bar-pct">${(ei.proportion * 100).toFixed(0)}%</div>
      `;
            emotionsEl.appendChild(bar);
        });
    }
    renderThemeList(assertElement(analysisThemes, "analysis-themes"), item.themes);
    if (item.trigger) {
        assertElement(analysisTriggerBlock, "analysis-trigger-block").classList.remove("hidden");
        assertElement(analysisTrigger, "analysis-trigger").textContent = item.trigger;
    }
    else {
        assertElement(analysisTriggerBlock, "analysis-trigger-block").classList.add("hidden");
    }
    if (item.physical_state) {
        assertElement(analysisPhysicalBlock, "analysis-physical-block").classList.remove("hidden");
        assertElement(analysisPhysicalState, "analysis-physical-state").textContent = item.physical_state;
    }
    else {
        assertElement(analysisPhysicalBlock, "analysis-physical-block").classList.add("hidden");
    }
    assertElement(analysisInsight, "analysis-insight").textContent = item.insight;
    if (item.compared_to_previous) {
        assertElement(analysisCompareBlock, "analysis-compare-block").classList.remove("hidden");
        assertElement(analysisCompared, "analysis-compared").textContent = item.compared_to_previous;
    }
    else {
        assertElement(analysisCompareBlock, "analysis-compare-block").classList.add("hidden");
    }
}
function renderHistory(items) {
    const container = assertElement(historyList, "history-list");
    container.innerHTML = "";
    if (items.length === 0) {
        container.innerHTML = `<div class="empty-state">还没有历史记录，先写下今天的第一篇日记吧。</div>`;
        return;
    }
    items.forEach((item) => {
        const card = document.createElement("article");
        card.className = "history-card";
        let subEmotions = "";
        if (item.emotions && item.emotions.length > 1) {
            subEmotions = `<div class="history-sub-emotions">${item.emotions
                .filter((e) => e.emotion !== item.emotion)
                .map((e) => `<span class="emotion-chip-sub">${e.emotion} ${(e.proportion * 100).toFixed(0)}%</span>`)
                .join("")}</div>`;
        }
        let triggerLine = item.trigger ? `<div class="history-trigger">触发：${item.trigger}</div>` : "";
        let compareLine = item.compared_to_previous ? `<div class="history-compare">${item.compared_to_previous}</div>` : "";
        card.innerHTML = `
      <div class="history-head">
        <div class="history-date">${formatDate(item.date)}</div>
        <span class="emotion-pill">${item.emotion}</span>
      </div>
      <div class="history-date">${item.emotion_group} / ${item.emotion_energy}</div>
      ${subEmotions}
      <div class="theme-list">${item.themes.map((theme) => `<span class="theme-chip">${theme}</span>`).join("")}</div>
      ${triggerLine}
      <p class="history-insight">${item.insight}</p>
      ${compareLine}
    `;
        container.appendChild(card);
    });
}
function renderSummary(summary) {
    assertElement(summaryEmpty, "summary-empty").classList.add("hidden");
    assertElement(summaryCard, "summary-card").classList.remove("hidden");
    assertElement(summaryRange, "summary-range").textContent = `${formatDate(summary.start_date)} - ${formatDate(summary.end_date)}`;
    assertElement(summaryCount, "summary-count").textContent = `${summary.total_entries} 篇记录`;
    assertElement(summaryIntensity, "summary-intensity").textContent = summary.average_intensity.toFixed(2);
    assertElement(summaryEmotions, "summary-emotions").textContent = summary.dominant_emotions.join(" / ") || "暂无";
    assertElement(summaryText, "summary-text").textContent = summary.summary;
    assertElement(summaryTrend, "summary-trend").textContent = summary.trend;
    assertElement(summarySuggestion, "summary-suggestion").textContent = summary.suggestion;
    const highlightsList = assertElement(summaryHighlights, "summary-highlights");
    highlightsList.innerHTML = "";
    summary.highlights.forEach((highlight) => {
        const item = document.createElement("li");
        item.textContent = highlight;
        highlightsList.appendChild(item);
    });
    renderThemeList(assertElement(summaryThemes, "summary-themes"), summary.top_themes);
}
function toggleSummaryFields() {
    const mode = assertElement(summaryMode, "summary-mode").value;
    const isCustom = mode === "custom";
    assertElement(customRangeFields, "custom-range-fields").classList.toggle("hidden", !isCustom);
    assertElement(anchorDateField, "anchor-date-field").classList.toggle("hidden", isCustom);
}
async function requestJson(url, options) {
    let response;
    try {
        response = await fetch(url, options);
    }
    catch {
        throw new Error("网络连接失败，请检查网络后重试。");
    }
    if (!response.ok) {
        let detail = "";
        try {
            const body = await response.json();
            detail = body.detail || "";
        }
        catch {
            // response body is not JSON
        }
        throw new Error(detail || `请求失败 (HTTP ${response.status})`);
    }
    return response.json();
}
async function loadHistory() {
    const data = await requestJson("/api/diary?limit=12");
    updateOverview(data.items);
    renderHistory(data.items);
    if (data.items[0]) {
        renderAnalysis(data.items[0]);
    }
}
async function loadSummary() {
    const mode = assertElement(summaryMode, "summary-mode").value;
    const params = new URLSearchParams();
    if (mode === "custom") {
        if (assertElement(summaryStartDate, "summary-start-date").value) {
            params.set("start_date", assertElement(summaryStartDate, "summary-start-date").value);
        }
        if (assertElement(summaryEndDate, "summary-end-date").value) {
            params.set("end_date", assertElement(summaryEndDate, "summary-end-date").value);
        }
    }
    else {
        params.set("period", mode);
        if (assertElement(summaryAnchorDate, "summary-anchor-date").value) {
            params.set("anchor_date", assertElement(summaryAnchorDate, "summary-anchor-date").value);
        }
    }
    const data = await requestJson(`/api/diary/summary?${params.toString()}`);
    renderSummary(data);
}
async function handleDiarySubmit(event) {
    event.preventDefault();
    assertElement(submitButton, "submit-entry").disabled = true;
    assertElement(formMessage, "form-message").textContent = "正在分析并保存...";
    try {
        const payload = {
            date: assertElement(diaryDateInput, "diary-date").value,
            content: assertElement(diaryContentInput, "diary-content").value,
        };
        const result = await requestJson("/api/diary", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });
        renderAnalysis(result);
        assertElement(formMessage, "form-message").textContent = "已保存，这条记录已经进入你的情绪轨迹。";
        assertElement(diaryContentInput, "diary-content").value = "";
        await loadHistory();
        await loadSummary();
        await loadCharts();
        await loadCalendar();
    }
    catch (error) {
        assertElement(formMessage, "form-message").textContent =
            error instanceof Error ? `提交失败：${error.message}` : "提交失败，请稍后再试。";
    }
    finally {
        assertElement(submitButton, "submit-entry").disabled = false;
    }
}
async function handleSummarySubmit(event) {
    event.preventDefault();
    try {
        await loadSummary();
    }
    catch (error) {
        assertElement(summaryEmpty, "summary-empty").classList.remove("hidden");
        assertElement(summaryEmpty, "summary-empty").textContent =
            error instanceof Error ? `生成失败：${error.message}` : "生成失败，请稍后再试。";
    }
}
function setDefaultDates() {
    const today = new Date().toISOString().slice(0, 10);
    assertElement(diaryDateInput, "diary-date").value = today;
    assertElement(summaryAnchorDate, "summary-anchor-date").value = today;
    assertElement(summaryEndDate, "summary-end-date").value = today;
    const start = new Date();
    start.setDate(start.getDate() - start.getDay() + 1);
    assertElement(summaryStartDate, "summary-start-date").value = start.toISOString().slice(0, 10);
}
const chartDays = document.querySelector("#chart-days");
const chartEmpty = document.querySelector("#chart-empty");
const chartArea = document.querySelector("#chart-area");
let intensityChart = null;
let distributionChart = null;
const EMOTION_COLORS = {
    joyful: "#e7bb6f", excited: "#d4952b", hopeful: "#b8c48a", proud: "#a0b870",
    grateful: "#8dad7a", relieved: "#7a9e6e", calm: "#6b9e5a", content: "#598a4a",
    focused: "#7eb8b0", thoughtful: "#5ea09a", confused: "#8a8a9e", numb: "#7a7a8e",
    anxious: "#c4683a", overwhelmed: "#b04a2e", frustrated: "#d4785e", angry: "#c83a2a",
    sad: "#6b8eb5", lonely: "#5a7a9e", disappointed: "#4a6a8e", guilty: "#6b6b8e",
    mixed: "#9e8a6e", unknown: "#aaa",
};
function getEmotionColor(emotion) {
    return EMOTION_COLORS[emotion] || "#aaa";
}
async function loadCharts() {
    const days = parseInt(assertElement(chartDays, "chart-days").value, 10);
    const data = await requestJson(`/api/diary/chart?days=${days}`);
    if (data.total_entries === 0) {
        assertElement(chartEmpty, "chart-empty").classList.remove("hidden");
        assertElement(chartArea, "chart-area").classList.add("hidden");
        return;
    }
    assertElement(chartEmpty, "chart-empty").classList.add("hidden");
    assertElement(chartArea, "chart-area").classList.remove("hidden");
    if (intensityChart)
        intensityChart.destroy();
    if (distributionChart)
        distributionChart.destroy();
    const labels = data.trend.map((d) => d.date.slice(5));
    const intensities = data.trend.map((d) => d.intensity);
    const pointColors = data.trend.map((d) => getEmotionColor(d.emotion));
    const ctx1 = document.querySelector("#intensity-chart").getContext("2d");
    intensityChart = new Chart(ctx1, {
        type: "line",
        data: {
            labels,
            datasets: [{
                    label: "情绪强度",
                    data: intensities,
                    borderColor: "#c4683a",
                    backgroundColor: "rgba(196, 104, 58, 0.08)",
                    pointBackgroundColor: pointColors,
                    pointRadius: 5,
                    pointHoverRadius: 7,
                    fill: true,
                    tension: 0.3,
                }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { min: 0, max: 1, ticks: { stepSize: 0.2 } },
            },
        },
    });
    const distLabels = data.distribution.map((d) => d.emotion);
    const distCounts = data.distribution.map((d) => d.count);
    const distColors = data.distribution.map((d) => getEmotionColor(d.emotion));
    const ctx2 = document.querySelector("#distribution-chart").getContext("2d");
    distributionChart = new Chart(ctx2, {
        type: "doughnut",
        data: {
            labels: distLabels,
            datasets: [{ data: distCounts, backgroundColor: distColors }],
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: "bottom", labels: { boxWidth: 12, padding: 12, font: { size: 11 } } },
            },
        },
    });
}
const calendarMonth = document.querySelector("#calendar-month");
const calendarArea = document.querySelector("#calendar-area");
const EMOTION_GROUP_COLORS = {
    positive: "#e7bb6f",
    neutral: "#7eb8b0",
    negative: "#c4683a",
    mixed: "#b8a08a",
    unknown: "#aaa",
};
function getEmotionGroup(emotion) {
    if (!emotion || emotion === "unknown")
        return "unknown";
    const positive = ["joyful", "excited", "hopeful", "proud", "grateful", "relieved", "calm", "content"];
    const neutral = ["focused", "thoughtful", "confused", "numb"];
    const negative = ["anxious", "overwhelmed", "frustrated", "angry", "sad", "lonely", "disappointed", "guilty"];
    if (positive.includes(emotion))
        return "positive";
    if (neutral.includes(emotion))
        return "neutral";
    if (negative.includes(emotion))
        return "negative";
    return "mixed";
}
async function loadCalendar() {
    const month = assertElement(calendarMonth, "calendar-month").value;
    const data = await requestJson(`/api/diary/calendar?month=${month}`);
    const container = assertElement(calendarArea, "calendar-area");
    const weekDays = ["日", "一", "二", "三", "四", "五", "六"];
    let html = weekDays.map((d) => `<div class="calendar-day-header">${d}</div>`).join("");
    const firstDate = new Date(data[0]?.date || `${month}-01`);
    const firstDow = firstDate.getDay();
    for (let i = 0; i < firstDow; i++) {
        html += `<div class="calendar-cell empty"></div>`;
    }
    data.forEach((d) => {
        if (d.has_entry) {
            const group = getEmotionGroup(d.emotion);
            const color = EMOTION_GROUP_COLORS[group] || "#aaa";
            const alpha = 0.3 + Math.min(d.intensity, 1.0) * 0.5;
            html += `<div class="calendar-cell has-entry" style="background:${color};opacity:${alpha.toFixed(2)}" title="${d.date}: ${d.emotion} (${d.intensity.toFixed(2)})">${d.day}</div>`;
        }
        else {
            html += `<div class="calendar-cell" style="background:rgba(120,95,67,0.04)">${d.day}</div>`;
        }
    });
    container.innerHTML = html;
}
async function bootstrap() {
    setDefaultDates();
    toggleSummaryFields();
    const today = new Date();
    const monthStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, "0")}`;
    assertElement(calendarMonth, "calendar-month").value = monthStr;
    assertElement(diaryForm, "diary-form").addEventListener("submit", handleDiarySubmit);
    assertElement(summaryForm, "summary-form").addEventListener("submit", handleSummarySubmit);
    assertElement(summaryMode, "summary-mode").addEventListener("change", toggleSummaryFields);
    assertElement(chartDays, "chart-days").addEventListener("change", loadCharts);
    assertElement(calendarMonth, "calendar-month").addEventListener("change", loadCalendar);
    await loadHistory();
    await loadSummary();
    await loadCharts();
    await loadCalendar();
}
void bootstrap();
