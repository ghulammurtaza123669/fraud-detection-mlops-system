const healthStatus = document.querySelector("#health-status");
const modelLoaded = document.querySelector("#model-loaded");
const modelVersion = document.querySelector("#model-version");
const lastProbability = document.querySelector("#last-probability");
const predictForm = document.querySelector("#predict-form");
const riskBadge = document.querySelector("#risk-badge");
const resultTitle = document.querySelector("#result-title");
const predictionValue = document.querySelector("#prediction-value");
const probabilityValue = document.querySelector("#probability-value");
const confidenceValue = document.querySelector("#confidence-value");
const responseVersion = document.querySelector("#response-version");
const rawResponse = document.querySelector("#raw-response");
const gaugeFill = document.querySelector("#gauge-fill");
const batchJson = document.querySelector("#batch-json");
const batchOutput = document.querySelector("#batch-output");

function percent(value) {
  return `${Math.round(Number(value) * 1000) / 10}%`;
}

function formPayload(form) {
  const data = new FormData(form);
  return {
    transaction_id: String(data.get("transaction_id")),
    amount: Number(data.get("amount")),
    oldbalance_org: Number(data.get("oldbalance_org")),
    newbalance_orig: Number(data.get("newbalance_orig")),
    oldbalance_dest: Number(data.get("oldbalance_dest")),
    newbalance_dest: Number(data.get("newbalance_dest")),
    transaction_type: String(data.get("transaction_type")),
    hour: Number(data.get("hour")),
  };
}

async function requestJson(url, options = {}) {
  const response = await fetch(url, options);
  const body = await response.json();
  if (!response.ok) {
    throw new Error(body.detail || `HTTP ${response.status}`);
  }
  return body;
}

async function loadHealth() {
  try {
    const health = await requestJson("/health");
    healthStatus.textContent = health.status.toUpperCase();
    modelLoaded.textContent = health.model_loaded ? "Yes" : "No";
    modelVersion.textContent = health.model_version;
  } catch (error) {
    healthStatus.textContent = "Error";
    modelLoaded.textContent = "Unknown";
    modelVersion.textContent = error.message;
  }
}

function renderPrediction(result) {
  const fraud = result.prediction === 1;
  riskBadge.textContent = fraud ? "Fraud" : "Legit";
  riskBadge.className = fraud ? "badge bad" : "badge good";
  resultTitle.textContent = fraud ? "High Risk Transaction" : "Low Risk Transaction";
  predictionValue.textContent = fraud ? "Fraudulent" : "Legitimate";
  probabilityValue.textContent = percent(result.fraud_probability);
  confidenceValue.textContent = percent(result.confidence_score);
  responseVersion.textContent = result.model_version;
  lastProbability.textContent = percent(result.fraud_probability);
  gaugeFill.style.width = percent(result.fraud_probability);
  gaugeFill.style.background = fraud ? "var(--bad)" : "var(--good)";
  rawResponse.textContent = JSON.stringify(result, null, 2);
}

predictForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  riskBadge.textContent = "Scoring";
  riskBadge.className = "badge neutral";
  try {
    const result = await requestJson("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(formPayload(predictForm)),
    });
    renderPrediction(result);
  } catch (error) {
    resultTitle.textContent = "Prediction Error";
    rawResponse.textContent = error.message;
  }
});

document.querySelector("#load-risky").addEventListener("click", () => {
  predictForm.transaction_id.value = `txn_${Date.now()}`;
  predictForm.transaction_type.value = "TRANSFER";
  predictForm.amount.value = "9800";
  predictForm.hour.value = "2";
  predictForm.oldbalance_org.value = "9800";
  predictForm.newbalance_orig.value = "0";
  predictForm.oldbalance_dest.value = "120";
  predictForm.newbalance_dest.value = "9920";
});

document.querySelector("#run-batch").addEventListener("click", async () => {
  batchOutput.textContent = "Running batch prediction...";
  try {
    const payload = JSON.parse(batchJson.value);
    const result = await requestJson("/batch-predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    batchOutput.textContent = JSON.stringify(result, null, 2);
  } catch (error) {
    batchOutput.textContent = error.message;
  }
});

document.querySelector("#refresh-health").addEventListener("click", loadHealth);
loadHealth();
