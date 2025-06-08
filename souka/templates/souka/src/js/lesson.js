// Для динамически добавленных элементов
document.body.addEventListener('click', function(e) {
  if (e.target.closest('.notes-toggle')) {
    e.target.closest('.lesson__notes').classList.toggle('active');
  }
});