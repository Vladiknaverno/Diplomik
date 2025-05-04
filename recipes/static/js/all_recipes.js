function initAllRecipes() {
    // === Відновлюємо відкриті категорії з localStorage ===
    const openedCategories = JSON.parse(localStorage.getItem('openedCategories') || '[]');

    document.querySelectorAll('.category-group').forEach((group, index) => {
        const mainCategory = group.querySelector('.main-category');
        const subcategories = group.querySelector('.subcategories');
        const anyChecked = subcategories.querySelector('input[type="checkbox"]:checked');

        if (anyChecked || openedCategories.includes(index)) {
            mainCategory.classList.add('active');
            subcategories.style.display = 'block';
        } else {
            mainCategory.classList.remove('active');
            subcategories.style.display = 'none';
        }

        // === Обробка кліку по головній категорії ===
        mainCategory.onclick = () => {
            const anyChecked = subcategories.querySelector('input[type="checkbox"]:checked');
            const currentIndex = [...document.querySelectorAll('.category-group')].indexOf(group);
            const currentOpened = JSON.parse(localStorage.getItem('openedCategories') || '[]');

            if (mainCategory.classList.contains('active')) {
                if (!anyChecked) {
                    mainCategory.classList.remove('active');
                    subcategories.style.display = 'none';
                    const updated = currentOpened.filter(i => i !== currentIndex);
                    localStorage.setItem('openedCategories', JSON.stringify(updated));
                }
            } else {
                mainCategory.classList.add('active');
                subcategories.style.display = 'block';
                if (!currentOpened.includes(currentIndex)) {
                    currentOpened.push(currentIndex);
                    localStorage.setItem('openedCategories', JSON.stringify(currentOpened));
                }
            }
        };
    });

    // === Автосабміт по зміні чекбоксів ===
    const form = document.getElementById('filtersForm');
    if (form) {
        form.querySelectorAll('input[type="checkbox"]').forEach(el => {
            el.addEventListener('change', () => {
                const group = el.closest('.category-group');
                const main = group.querySelector('.main-category');
                const subs = group.querySelector('.subcategories');
                const index = [...document.querySelectorAll('.category-group')].indexOf(group);
                const opened = JSON.parse(localStorage.getItem('openedCategories') || '[]');

                main.classList.add('active');
                subs.style.display = 'block';

                if (!opened.includes(index)) {
                    opened.push(index);
                    localStorage.setItem('openedCategories', JSON.stringify(opened));
                }

                form.dispatchEvent(new Event('submit', { bubbles: true }));
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', initAllRecipes);
document.body.addEventListener('htmx:afterSwap', () => {
    initAllRecipes();
});
