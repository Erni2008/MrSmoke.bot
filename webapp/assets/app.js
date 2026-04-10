const tg = window.Telegram?.WebApp;
const form = document.getElementById("order-form");
const statusText = document.getElementById("status-text");
const progressLabel = document.getElementById("progress-label");
const progressBar = document.getElementById("progress-bar");
const serviceInput = document.getElementById("service_type");
const attachmentsInput = document.getElementById("attachments");
const uploadStatus = document.getElementById("upload-status");
const uploadPreview = document.getElementById("upload-preview");
const clearDraftButton = document.getElementById("clear-draft");
const serviceCards = [...document.querySelectorAll(".service-card")];
const fillButtons = [...document.querySelectorAll("[data-fill-target]")];
const textareas = [...document.querySelectorAll("textarea")];

const DRAFT_KEY = "mcoc_order_draft_v2";
const uploadedFiles = [];
const requiredFields = [
  "service_type",
  "target_content",
  "content_info",
  "game_nickname",
  "deadline",
  "priority_factors",
];

if (tg) {
  tg.ready();
  tg.expand();
  tg.MainButton.setText("Отправить заявку");
  tg.MainButton.show();
}

const setStatus = (text) => {
  statusText.textContent = text;
};

const autosize = (textarea) => {
  textarea.style.height = "auto";
  textarea.style.height = `${textarea.scrollHeight}px`;
};

textareas.forEach((textarea) => {
  autosize(textarea);
  textarea.addEventListener("input", () => autosize(textarea));
});

const getFormPayload = () => Object.fromEntries(new FormData(form).entries());

const saveDraft = () => {
  const payload = getFormPayload();
  const draft = {
    ...payload,
    attachments: uploadedFiles,
  };
  localStorage.setItem(DRAFT_KEY, JSON.stringify(draft));
};

const restoreDraft = () => {
  const raw = localStorage.getItem(DRAFT_KEY);
  if (!raw) {
    return;
  }

  try {
    const draft = JSON.parse(raw);
    Object.entries(draft).forEach(([key, value]) => {
      if (key === "attachments" || typeof value !== "string") {
        return;
      }
      const field = form.elements.namedItem(key);
      if (field) {
        field.value = value;
      }
    });

    if (Array.isArray(draft.attachments)) {
      uploadedFiles.splice(0, uploadedFiles.length, ...draft.attachments);
      renderUploads();
    }
  } catch {
    localStorage.removeItem(DRAFT_KEY);
  }
};

const getFilledCount = () => {
  const payload = getFormPayload();
  return requiredFields.filter((field) => String(payload[field] || "").trim().length > 0).length;
};

const updateProgress = () => {
  const filledCount = getFilledCount();
  const percent = Math.round((filledCount / requiredFields.length) * 100);

  progressLabel.textContent = `${percent}%`;
  progressBar.style.width = `${percent}%`;

  if (percent === 100) {
    setStatus(
      uploadedFiles.length > 0
        ? `Форма готова. Скрины прикреплены: ${uploadedFiles.length}`
        : "Форма готова. Если можешь, добавь скрины персов."
    );
    return true;
  }

  setStatus(`Заполнено ${filledCount} из ${requiredFields.length} обязательных блоков`);
  return false;
};

const renderUploads = () => {
  uploadPreview.innerHTML = "";

  if (!uploadedFiles.length) {
    uploadStatus.textContent = "Файлы не загружены";
    saveDraft();
    return;
  }

  uploadStatus.textContent = `Загружено файлов: ${uploadedFiles.length}`;

  uploadedFiles.forEach((file, index) => {
    const card = document.createElement("div");
    card.className = "preview-card";
    card.innerHTML = `
      <img src="${file.url}" alt="${file.filename}" />
      <div class="preview-card__meta">
        <span>${file.filename}</span>
        <button type="button" data-remove-index="${index}">Убрать</button>
      </div>
    `;
    uploadPreview.appendChild(card);
  });

  saveDraft();
};

uploadPreview.addEventListener("click", (event) => {
  const button = event.target.closest("[data-remove-index]");
  if (!button) {
    return;
  }

  const index = Number(button.dataset.removeIndex);
  uploadedFiles.splice(index, 1);
  renderUploads();
  updateProgress();
});

const setService = (value) => {
  serviceInput.value = value;
  serviceCards.forEach((card) => {
    card.classList.toggle("is-active", card.dataset.service === value);
  });
  saveDraft();
  updateProgress();
};

serviceCards.forEach((card) => {
  card.addEventListener("click", () => {
    setService(card.dataset.service);
  });
});

fillButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const target = document.getElementById(button.dataset.fillTarget);
    if (!target) {
      return;
    }

    const value = button.dataset.fillValue || "";
    const mode = button.dataset.fillMode || "replace";

    if (mode === "append" && target.value.trim()) {
      const separator = target.value.trim().endsWith(".") ? " " : ". ";
      target.value = `${target.value.trim()}${separator}${value}`;
    } else {
      target.value = value;
    }

    target.dispatchEvent(new Event("input", { bubbles: true }));
    target.focus();
  });
});

form.addEventListener("input", () => {
  saveDraft();
  updateProgress();
});

const uploadSingleFile = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("/api/upload", {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    throw new Error("upload_failed");
  }

  const data = await response.json();
  uploadedFiles.push(data);
};

attachmentsInput.addEventListener("change", async (event) => {
  const files = [...event.target.files];
  if (!files.length) {
    return;
  }

  uploadStatus.textContent = "Загрузка файлов...";

  try {
    for (const file of files) {
      await uploadSingleFile(file);
    }
    renderUploads();
    updateProgress();
  } catch {
    uploadStatus.textContent = "Не удалось загрузить один или несколько файлов";
  } finally {
    attachmentsInput.value = "";
  }
});

clearDraftButton.addEventListener("click", () => {
  localStorage.removeItem(DRAFT_KEY);
  form.reset();
  uploadedFiles.splice(0, uploadedFiles.length);
  setService("Прохождение квестов");
  textareas.forEach((textarea) => autosize(textarea));
  renderUploads();
  updateProgress();
});

const submit = () => {
  if (!updateProgress()) {
    if (tg) {
      tg.showAlert("Заполни обязательные поля.");
    }
    return;
  }

  if (!tg) {
    setStatus("Открой форму именно внутри Telegram.");
    return;
  }

  const payload = {
    ...getFormPayload(),
    attachments: uploadedFiles,
  };

  tg.sendData(JSON.stringify(payload));
  localStorage.removeItem(DRAFT_KEY);
  setStatus("Заявка и скрины отправлены.");
};

if (tg) {
  tg.onEvent("mainButtonClicked", submit);
}

restoreDraft();
setService(serviceInput.value || "Прохождение квестов");
updateProgress();
