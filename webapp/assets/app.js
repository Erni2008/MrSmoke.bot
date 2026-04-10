const tg = window.Telegram?.WebApp;
const form = document.getElementById("order-form");
const statusText = document.getElementById("status-text");
const progressLabel = document.getElementById("progress-label");
const progressBar = document.getElementById("progress-bar");
const serviceInput = document.getElementById("service_type");
const serviceCards = [...document.querySelectorAll(".service-card")];

const requiredFields = [
  "customer_name",
  "service_type",
  "game_nickname",
  "contact",
  "deadline",
  "details",
];

if (tg) {
  tg.ready();
  tg.expand();
  tg.MainButton.setText("Отправить заказ");
  tg.MainButton.show();
}

const setStatus = (text) => {
  statusText.textContent = text;
};

const getFormPayload = () => Object.fromEntries(new FormData(form).entries());

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
    setStatus("Форма заполнена. Можно отправлять заявку.");
    return true;
  }

  setStatus(`Заполнено ${filledCount} из ${requiredFields.length} полей`);
  return false;
};

const setService = (value) => {
  serviceInput.value = value;
  serviceCards.forEach((card) => {
    card.classList.toggle("is-active", card.dataset.service === value);
  });
  updateProgress();
};

serviceCards.forEach((card) => {
  card.addEventListener("click", () => {
    setService(card.dataset.service);
  });
});

form.addEventListener("input", updateProgress);

const submit = () => {
  if (!updateProgress()) {
    if (tg) {
      tg.showAlert("Заполни все поля формы.");
    }
    return;
  }

  if (!tg) {
    setStatus("Открой mini app внутри Telegram.");
    return;
  }

  tg.sendData(JSON.stringify(getFormPayload()));
  setStatus("Заявка отправлена администратору.");
};

if (tg) {
  tg.onEvent("mainButtonClicked", submit);
}

updateProgress();
