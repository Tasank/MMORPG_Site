// Это обработчик события
document.addEventListener("DOMContentLoaded", function() {
  const container = document.querySelector('.delete-container');
  container.addEventListener('animationend', function() {
    container.classList.add('animated');
  });
});
