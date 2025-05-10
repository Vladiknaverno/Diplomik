function initCategorySelect() {
  const $select = $('#id_categories');

  if (!$select.length || $select.hasClass('select2-hidden-accessible')) return;

  $select.select2({
    placeholder: 'Оберіть категорії...',
    allowClear: true,
    width: '100%',
    minimumInputLength: 1,
    closeOnSelect: false,
    dropdownParent: $('body'),
    ajax: {
      url: '/search_categories/',
      dataType: 'json',
      delay: 250,
      data: params => ({ term: params.term }),
      processResults: data => ({
        results: data.map(item => ({
          id: item.id,
          text: item.name
        }))
      }),
      cache: true
    }
  });

  // Після вибору — очищає інпут пошуку
  $select.on('select2:select', function () {
    setTimeout(() => {
     $('.select2-search__field').val('');
     $select.select2('close'); // ✅ закриває dropdown після вибору
    }, 0);
  });
}

function initImageUpload() {
  const area = document.getElementById('imageUploadArea');
  const input = document.getElementById('image-upload-input');
  const preview = document.getElementById('imagePreview');
  const previewContainer = document.getElementById('imagePreviewContainer');
  const removeBtn = document.getElementById('removeImageBtn');
  const fileNameDisplay = document.getElementById('fileName');

  if (!area || !input || area.dataset.bound === 'true') return;
  area.dataset.bound = 'true'; // ✅ щоб не дублювалось

  area.addEventListener('click', () => input.click());

  input.addEventListener('change', function () {
    if (this.files && this.files[0]) {
      const file = this.files[0];
      fileNameDisplay.textContent = file.name;

      const reader = new FileReader();
      reader.onload = function (e) {
        preview.style.backgroundImage = `url(${e.target.result})`;
        area.style.display = 'none';
        previewContainer.style.display = 'block';
      };
      reader.readAsDataURL(file);
    }
  });

  removeBtn.addEventListener('click', function (e) {
    e.stopPropagation();
    input.value = '';
    preview.style.backgroundImage = '';
    fileNameDisplay.textContent = '';
    previewContainer.style.display = 'none';
    area.style.display = 'flex';
  });

  area.addEventListener('dragover', function (e) {
    e.preventDefault();
    this.classList.add('dragover');
  });

  area.addEventListener('dragleave', function () {
    this.classList.remove('dragover');
  });

  area.addEventListener('drop', function (e) {
    e.preventDefault();
    this.classList.remove('dragover');

    if (e.dataTransfer.files.length && e.dataTransfer.files[0].type.startsWith('image/')) {
      input.files = e.dataTransfer.files;
      const event = new Event('change');
      input.dispatchEvent(event);
    }
  });
}

// ✅ Працює при звичайному завантаженні
document.addEventListener('DOMContentLoaded', () => {
  initCategorySelect();
  initImageUpload();
});

// ✅ Працює при HTMX вставленні (після \"Створити рецепт\")
document.body.addEventListener('htmx:afterSwap', function (e) {
  if (e.target.closest('form') || e.target.id === 'main-content') {
    setTimeout(() => {
      initCategorySelect();
      initImageUpload();
    }, 0);
  }
});
