function initSaveButtons() {
  document.querySelectorAll('.save-btn').forEach(btn => {
    btn.onclick = function () {
      const recipeId = this.dataset.recipeId;
      const isSaved = this.classList.contains('saved');
      const url = isSaved ? `/recipe/${recipeId}/unsave/` : `/recipe/${recipeId}/save/`;

      fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
      })
      .then(res => res.json())
      .then(data => {
        this.classList.toggle('saved');
        this.innerHTML = data.saved
          ? '<i class="fas fa-bookmark"></i> Збережено'
          : '<i class="far fa-bookmark"></i> Зберегти';
      });
    };
  });
}

function initLikeButtons() {
  document.querySelectorAll('.like-btn').forEach(btn => {
    btn.onclick = function () {
      const recipeId = this.dataset.recipeId;
      const likeCount = this.querySelector('.like-count');

      fetch(`/recipe/${recipeId}/like/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
          'Content-Type': 'application/json'
        },
        credentials: 'same-origin'
      })
      .then(response => response.json())
      .then(data => {
        this.classList.toggle('liked');
        likeCount.textContent = data.like_count;
      });
    };
  });
}
