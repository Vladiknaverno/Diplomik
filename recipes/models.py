from django.conf import settings
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models
from django.utils.text import slugify

class User(AbstractUser):
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)

    saved_recipes = models.ManyToManyField(
        'Recipe',
        related_name='saved_by_users',
        blank=True
    )

    class Meta:
        db_table = 'recipes_user'

    def __str__(self):
        return self.username


# models.py
class Category(models.Model):
    TYPE_CHOICES = [
        ('BREAKFAST', 'Сніданки'),
        ('MAIN', 'Основні страви'),
        ('DESSERT', 'Десерти'),
        ('DRINK', 'Напої'),
        ('BAKING', 'Випічка'),
        ('SNACK', 'Закуски'),
        ('KIDS', 'Для дітей'),
        ('DIET', 'Дієти'),
        ('HOLIDAY', 'Свята'),
    ]

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='children',
        on_delete=models.CASCADE
    )
    category_type = models.CharField(
        max_length=10,
        choices=TYPE_CHOICES,
        default='MAIN'
    )
    icon = models.CharField(max_length=30, default='fa-utensils')  # залишаємо для старої іконки
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)  # Додаємо поле для завантаження картинки 🔥

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['category_type', 'name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Category.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

class Recipe(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField()
    steps = models.TextField()
    image = models.ImageField(upload_to='recipes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='recipes'
    )
    categories = models.ManyToManyField(Category, related_name='recipes')
    cooking_time = models.PositiveIntegerField(
        verbose_name="Час приготування (хвилин)",
        help_text="Час у хвилинах",
        null=True,
        blank=True
    )
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Like',
        related_name='liked_recipes',
        blank=True
    )
    def __str__(self):
        return self.title

    rating = models.FloatField(default=0)  # середній рейтинг
    ratings_count = models.PositiveIntegerField(default=0)  # кількість оцінок
    @property
    def like_count(self):
        return self.likes.count()

    def is_liked_by(self, user):
        if not user.is_authenticated:
            return False
        return self.likes.filter(id=user.id).exists()

class Like(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'recipe')  # Користувач може лайкнути рецепт лише один раз

class Rating(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='ratings')
    value = models.PositiveSmallIntegerField()  # 1-5

    class Meta:
        unique_together = ('user', 'recipe')

class Comment(models.Model):
    recipe = models.ForeignKey('Recipe', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Коментар від {self.user.username} до {self.recipe.title}'