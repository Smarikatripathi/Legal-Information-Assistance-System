document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("[data-bs-toggle='tooltip']").forEach((el) => {
    if (window.bootstrap) new bootstrap.Tooltip(el);
  });
});
