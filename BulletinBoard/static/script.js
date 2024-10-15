// Это обработчик события анимации выдвигания сверху изображения при удалении объявления.
document.addEventListener("DOMContentLoaded", function() {
  const container = document.querySelector('.delete-container');
  container.addEventListener('animationend', function() {
    container.classList.add('animated');
  });
});
