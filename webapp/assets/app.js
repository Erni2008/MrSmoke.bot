const tg = window.Telegram?.WebApp;
const form = document.getElementById("order-form");
const statusText = document.getElementById("status-text");
const serviceInput = document.getElementById("service_type");
const chips = [...document.querySelectorAll(".service-chip")];

if (tg) {
  tg.ready();
  tg.expand();
  tg.MainButton.setText("Отправить заказ");
  tg.MainButton.show();
}

const setStatus = (text) => {
  statusText.textContent = text;
};

const validate = () => {
  const data = new FormData(form);
  const requiredFields = [
    "customer_name",
    "service_type",
    "game_nickname",
    "contact",
    "deadline",
    "details",
  ];

  return requiredFields.every((field) => String(data.get(field) || "").trim().length > 0);
};

chips.forEach((chip) => {
  chip.addEventListener("click", () => {
    chips.forEach((node) => node.classList.remove("is-active"));
    chip.classList.add("is-active");
    serviceInput.value = chip.dataset.service;
    setStatus(`Выбрана услуга: ${chip.dataset.service}`);
  });
});

form.addEventListener("input", () => {
  setStatus(validate() ? "Форма готова к отправке" : "Заполни все поля, чтобы отправить заявку");
});

const submit = () => {
  if (!validate()) {
    setStatus("Не все поля заполнены");
    if (tg) {
      tg.showAlert("Заполни все поля формы.");
    }
    return;
  }

  if (!tg) {
    setStatus("Открой форму внутри Telegram");
    return;
  }

  const payload = Object.fromEntries(new FormData(form).entries());
  tg.sendData(JSON.stringify(payload));
  setStatus("Заявка отправлена");
};

if (tg) {
  tg.onEvent("mainButtonClicked", submit);
}
