type AnalysisResponse = {
  id: number;
  date: string;
  emotion: string;
  emotion_group: string;
  emotion_valence: string;
  emotion_energy: string;
  intensity: number;
  themes: string[];
  insight: string;
  created_at: string;
};

type DiaryListResponse = {
  items: AnalysisResponse[];
};

type DiarySummaryResponse = {
  start_date: string;
  end_date: string;
  total_entries: number;
  average_intensity: number;
  top_themes: string[];
  dominant_emotions: string[];
  summary: string;
  trend: string;
  highlights: string[];
  suggestion: string;
};

const diaryForm = document.querySelector<HTMLFormElement>("#diary-form");
const summaryForm = document.querySelector<HTMLFormElement>("#summary-form");
const diaryDateInput = document.querySelector<HTMLInputElement>("#diary-date");
const diaryContentInput = document.querySelector<HTMLTextAreaElement>("#diary-content");
const submitButton = document.querySelector<HTMLButtonElement>("#submit-entry");
const formMessage = document.querySelector<HTMLElement>("#form-message");

const analysisEmpty = document.querySelector<HTMLElement>("#analysis-empty");
const analysisCard = document.querySelector<HTMLElement>("#analysis-card");
const analysisDate = document.querySelector<HTMLElement>("#analysis-date");
const analysisEmotion = document.querySelector<HTMLElement>("#analysis-emotion");
const analysisIntensityText = document.querySelector<HTMLElement>("#analysis-intensity-text");
const analysisIntensityBar = document.querySelector<HTMLElement>("#analysis-intensity-bar");
const analysisThemes = document.querySelector<HTMLElement>("#analysis-themes");
const analysisInsight = document.querySelector<HTMLElement>("#analysis-insight");
const analysisMeta = document.querySelector<HTMLElement>("#analysis-meta");

const summaryMode = document.querySelector<HTMLSelectElement>("#summary-mode");
const summaryAnchorDate = document.querySelector<HTMLInputElement>("#summary-anchor-date");
const summaryStartDate = document.querySelector<HTMLInputElement>("#summary-start-date");
const summaryEndDate = document.querySelector<HTMLInputElement>("#summary-end-date");
const anchorDateField = document.querySelector<HTMLElement>("#anchor-date-field");
const customRangeFields = document.querySelector<HTMLElement>("#custom-range-fields");
const summaryEmpty = document.querySelector<HTMLElement>("#summary-empty");
const summaryCard = document.querySelector<HTMLElement>("#summary-card");
const summaryRange = document.querySelector<HTMLElement>("#summary-range");
const summaryCount = document.querySelector<HTMLElement>("#summary-count");
const summaryIntensity = document.querySelector<HTMLElement>("#summary-intensity");
const summaryEmotions = document.querySelector<HTMLElement>("#summary-emotions");
const summaryText = document.querySelector<HTMLElement>("#summary-text");
const summaryTrend = document.querySelector<HTMLElement>("#summary-trend");
const summaryHighlights = document.querySelector<HTMLElement>("#summary-highlights");
const summaryThemes = document.querySelector<HTMLElement>("#summary-themes");
const summarySuggestion = document.querySelector<HTMLElement>("#summary-suggestion");

const historyList = document.querySelector<HTMLElement>("#history-list");
const entryCount = document.querySelector<HTMLElement>("#entry-count");
const topEmotion = document.querySelector<HTMLElement>("#top-emotion");
const topTheme = document.querySelector<HTMLElement>("#top-theme");

function assertElement<T>(element: T | null, name: string): T {
  if (!element) {
    throw new Error(`Missing required element: ${name}`);
  }

  return element;
}

function renderThemeList(container: HTMLElement, values: string[]) {
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

function formatDate(value: string) {
  return new Date(value).toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });
}

function updateOverview(items: AnalysisResponse[]) {
  assertElement(entryCount, "entry-count").textContent = String(items.length);
  assertElement(topEmotion, "top-emotion").textContent = items[0]?.emotion ?? "-";
  assertElement(topTheme, "top-theme").textContent = items[0]?.themes[0] ?? "-";
}

function renderAnalysis(item: AnalysisResponse) {
  assertElement(analysisEmpty, "analysis-empty").classList.add("hidden");
  assertElement(analysisCard, "analysis-card").classList.remove("hidden");
  assertElement(analysisDate, "analysis-date").textContent = formatDate(item.date);
  assertElement(analysisEmotion, "analysis-emotion").textContent = item.emotion;
  assertElement(
    analysisMeta,
    "analysis-meta",
  ).textContent = `${item.emotion_group} / ${item.emotion_valence} / ${item.emotion_energy}`;
  assertElement(analysisIntensityText, "analysis-intensity-text").textContent = item.intensity.toFixed(2);
  assertElement(analysisIntensityBar, "analysis-intensity-bar").style.width = `${Math.max(
    0,
    Math.min(item.intensity, 1),
  ) * 100}%`;
  renderThemeList(assertElement(analysisThemes, "analysis-themes"), item.themes);
  assertElement(analysisInsight, "analysis-insight").textContent = item.insight;
}

function renderHistory(items: AnalysisResponse[]) {
  const container = assertElement(historyList, "history-list");
  container.innerHTML = "";

  if (items.length === 0) {
    container.innerHTML = `<div class="empty-state">还没有历史记录，先写下今天的第一篇日记吧。</div>`;
    return;
  }

  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "history-card";
    card.innerHTML = `
      <div class="history-head">
        <div class="history-date">${formatDate(item.date)}</div>
        <span class="emotion-pill">${item.emotion}</span>
      </div>
      <div class="history-date">${item.emotion_group} / ${item.emotion_energy}</div>
      <div class="theme-list">${item.themes.map((theme) => `<span class="theme-chip">${theme}</span>`).join("")}</div>
      <p class="history-insight">${item.insight}</p>
    `;
    container.appendChild(card);
  });
}

function renderSummary(summary: DiarySummaryResponse) {
  assertElement(summaryEmpty, "summary-empty").classList.add("hidden");
  assertElement(summaryCard, "summary-card").classList.remove("hidden");
  assertElement(summaryRange, "summary-range").textContent = `${formatDate(summary.start_date)} - ${formatDate(
    summary.end_date,
  )}`;
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

async function requestJson<T>(url: string, options?: RequestInit): Promise<T> {
  const response = await fetch(url, options);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "请求失败");
  }

  return response.json() as Promise<T>;
}

async function loadHistory() {
  const data = await requestJson<DiaryListResponse>("/api/diary?limit=12");
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
  } else {
    params.set("period", mode);
    if (assertElement(summaryAnchorDate, "summary-anchor-date").value) {
      params.set("anchor_date", assertElement(summaryAnchorDate, "summary-anchor-date").value);
    }
  }

  const data = await requestJson<DiarySummaryResponse>(`/api/diary/summary?${params.toString()}`);
  renderSummary(data);
}

async function handleDiarySubmit(event: SubmitEvent) {
  event.preventDefault();

  assertElement(submitButton, "submit-entry").disabled = true;
  assertElement(formMessage, "form-message").textContent = "正在分析并保存...";

  try {
    const payload = {
      date: assertElement(diaryDateInput, "diary-date").value,
      content: assertElement(diaryContentInput, "diary-content").value,
    };
    const result = await requestJson<AnalysisResponse>("/api/diary", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    renderAnalysis(result);
    assertElement(formMessage, "form-message").textContent = "已保存，这条记录已经进入你的情绪轨迹。";
    assertElement(diaryContentInput, "diary-content").value = "";
    await loadHistory();
    await loadSummary();
  } catch (error) {
    assertElement(formMessage, "form-message").textContent =
      error instanceof Error ? `提交失败：${error.message}` : "提交失败，请稍后再试。";
  } finally {
    assertElement(submitButton, "submit-entry").disabled = false;
  }
}

async function handleSummarySubmit(event: SubmitEvent) {
  event.preventDefault();
  try {
    await loadSummary();
  } catch (error) {
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

async function bootstrap() {
  setDefaultDates();
  toggleSummaryFields();
  assertElement(diaryForm, "diary-form").addEventListener("submit", handleDiarySubmit);
  assertElement(summaryForm, "summary-form").addEventListener("submit", handleSummarySubmit);
  assertElement(summaryMode, "summary-mode").addEventListener("change", toggleSummaryFields);

  await loadHistory();
  await loadSummary();
}

void bootstrap();
