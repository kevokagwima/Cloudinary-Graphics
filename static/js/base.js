const btn = document.querySelector(".btn");
const input = document.querySelector("#name");

btn.addEventListener("click", () => {
  if (input.value) {
    btn.classList.toggle("btn--loading");
    btn.disabled = true;
    btn.form.submit();
  }
});
