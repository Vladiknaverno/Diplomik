
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category, Recipe, Comment, Rating, Follow, Notification
from django.core.paginator import Paginator
from .forms import RecipeForm, LoginForm, RegisterForm
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.db.models import Avg
import json
from django.contrib.auth import get_user_model
User = get_user_model()
from django.views.decorators.http import require_POST

@login_required
def add_recipe(request):
    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES)
        if form.is_valid():
            recipe = form.save(commit=False)
            recipe.author = request.user
            recipe.save()
            form.save_m2m()

            # ✅ Створюємо сповіщення для підписників
            followers = Follow.objects.filter(following=request.user).values_list('follower', flat=True)
            Notification.objects.bulk_create([
                Notification(
                    recipient_id=follower_id,
                    message=f"{request.user.username} додав новий рецепт: {recipe.title}",
                    recipe=recipe  # 🆕
                )
                for follower_id in followers
            ])

            return redirect('recipe_detail', pk=recipe.pk)
    else:
        form = RecipeForm()

    context = {'form': form}

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'recipes/partials/add_recipe_content.html', context)

    return render(request, 'recipes/add_recipe.html', context)

def recipe_list(request):
    recipes = Recipe.objects.all().order_by('-created_at')[:6]
    categories = Category.objects.filter(parent__isnull=True)  # основні категорії для каруселі

    context = {
        'recipes': recipes,
        'categories': categories,
    }

    if request.headers.get('HX-Request') == 'true':
        return render(request, 'recipes/partials/recipe_list_content.html', context)

    return render(request, 'recipes/recipe_list.html', context)



def recipe_detail(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    comments = recipe.comments.all().order_by('-created_at')  # завантажити всі коментарі

    if request.method == 'POST':
        if request.user.is_authenticated:
            text = request.POST.get('comment_text')
            if text:
                Comment.objects.create(recipe=recipe, user=request.user, text=text)
                return redirect('recipe_detail', pk=pk)

    recipe.ingredients_as_list = recipe.ingredients.split('\n')
    recipe.steps_as_list = recipe.steps.split('\n')

    context = {
        'recipe': recipe,
        'is_saved': recipe in request.user.saved_recipes.all() if request.user.is_authenticated else False,
        'comments': comments,
    }
    return render(request, 'recipes/recipe_detail.html', context)


def all_recipes(request):
    recipes = Recipe.objects.all()
    selected_categories = request.GET.getlist('category')
    query = request.GET.get('q')
    if query:
        recipes = recipes.filter(title__icontains=query)

    if selected_categories:
        selected_category_ids = []

        for cat_id in selected_categories:
            try:
                category = Category.objects.get(id=cat_id)
                if category.parent is None:
                    # Це основна категорія → беремо ВСІ підкатегорії
                    child_ids = category.children.values_list('id', flat=True)
                    selected_category_ids.extend(child_ids)
                else:
                    selected_category_ids.append(category.id)
            except Category.DoesNotExist:
                pass

        if selected_category_ids:
            recipes = recipes.filter(categories__id__in=selected_category_ids).distinct()
        else:
            # Якщо підкатегорій нема — не показувати нічого
            recipes = Recipe.objects.none()

    sort = request.GET.get('sort', 'newest')
    if sort == 'popular':
        recipes = recipes.order_by('-rating', '-ratings_count', '-created_at')
    elif sort == 'oldest':
        recipes = recipes.order_by('created_at')
    else:
        recipes = recipes.order_by('-created_at')

    main_categories = Category.objects.filter(parent__isnull=True).order_by('name')

    paginator = Paginator(recipes, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'main_categories': main_categories,
        'selected_categories': selected_categories,
        'sort': sort,
    }

    if request.headers.get('HX-Request'):
        return render(request, 'recipes/partials/all_recipes_content.html', context)
    else:
        return render(request, 'recipes/all_recipes.html', context)


def all_categories(request):
    # Фільтрація по категоріях (можна вибирати кілька)
    selected_categories = request.GET.getlist('category')
    recipes = Recipe.objects.all()

    if selected_categories:
        recipes = recipes.filter(categories__slug__in=selected_categories).distinct()
   # Отримуємо всі категорії, які не є дочірніми (основні категорії)
    main_categories = Category.objects.filter(parent__isnull=True)

    # Групуємо категорії за типами (якщо потрібно)
    # У цьому прикладі просто передаємо всі основні категорії
    context = {
        'main_categories': {
            'Основні категорії': main_categories
        }
    }
    return render(request, 'recipes/categories.html', context)


def category_view(request, slug):
    category = get_object_or_404(Category, slug=slug)

    if category.children.exists():
        # Якщо є підкатегорії — шукаємо рецепти по всіх дочірніх категоріях
        recipes = Recipe.objects.filter(categories__in=category.children.all()).distinct()
    else:
        # Якщо підкатегорій немає — шукаємо по самій категорії
        recipes = Recipe.objects.filter(categories=category)

    context = {
        'category': category,
        'recipes': recipes,
        'subcategories': category.children.all() if hasattr(category, 'children') else None
    }
    return render(request, 'recipes/category_detail.html', context)

@login_required
def report_bug(request):
    return redirect("https://forms.gle/твоя-форма")  # заміни на свою URL

# Відображення сповіщень (поки що тестові)
@login_required
def notifications(request):
    # Отримати всі сповіщення
    notes = request.user.notifications.order_by('-created_at')[:20]

    # ✅ Відмітити їх як прочитані
    request.user.notifications.filter(is_read=False).update(is_read=True)

    return render(request, 'recipes/notifications.html', {'notifications': notes})

@require_POST
@login_required
def clear_notifications(request):
    request.user.notifications.all().delete()
    if request.headers.get('HX-Request'):
        return render(request, 'recipes/partials/notifications_dropdown.html', {'notifications': []})
    return redirect('notifications')

@login_required
def notifications_dropdown(request):
    notes = request.user.notifications.order_by('-created_at')[:10]
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, 'recipes/partials/notifications_dropdown.html', {'notifications': notes})


@login_required
def toggle_follow(request, username):
    author = get_object_or_404(User, username=username)

    if author == request.user:
        return redirect('user_profile', username=username)

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=author
    )

    if not created:
        follow.delete()

    return redirect('user_profile', username=username)

@login_required
def user_profile(request, username):
    author = get_object_or_404(User, username=username)
    recipes = author.recipes.all()
    avg_rating = recipes.aggregate(avg=Avg('rating'))['avg'] or 0
    avg_rating = round(avg_rating, 1)
    is_following = Follow.objects.filter(follower=request.user, following=author).exists()

    context = {
        'author': author,
        'recipes': recipes,
        'avg_rating': avg_rating,
        'is_following': is_following,
    }

    if request.headers.get("Hx-Request") == "true":
        # HTMX запит → повертаємо тільки вміст
        html = render_to_string("recipes/partials/user_profile_content.html", context, request=request)
        return HttpResponse(html)
    else:
        # Повна сторінка (напряму через URL)
        return render(request, "recipes/user_profile.html", context)

def contacts(request):
    template = 'recipes/contacts.html'
    if request.headers.get('HX-Request'):
        template = 'recipes/partials/contacts_content.html'
    return render(request, template)

def about(request):
    template = 'recipes/about.html'
    if request.headers.get('HX-Request'):
        template = 'recipes/partials/about_content.html'
    return render(request, template)

def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('recipe_list')
    else:
        form = RegisterForm()

    template = 'registration/register.html'
    if request.headers.get('HX-Request'):
        template = 'registration/register_content.html'

    return render(request, template, {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if not form.cleaned_data['remember_me']:
                request.session.set_expiry(0)
            return redirect('recipe_list')
    else:
        form = LoginForm()

    template = 'registration/login.html'
    if request.headers.get('HX-Request'):
        template = 'registration/login_content.html'

    return render(request, template, {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('recipe_list')

@login_required
def profile(request):
    user = request.user
    recipes = user.recipes.all()
    saved_recipes = user.saved_recipes.all()

    avg_rating = user.recipes.aggregate(avg=Avg('rating'))['avg'] or 0
    avg_rating = round(avg_rating, 1)
    total_comments = Comment.objects.filter(user=user).count()

    context = {
        'user': user,
        'recipes': recipes,
        'saved_recipes': saved_recipes,
        'avg_rating': avg_rating,
        'total_comments': total_comments,
    }

    if request.headers.get("HX-Request") == "true":
        return render(request, 'recipes/partials/profile_content.html', context)

    return render(request, 'recipes/profile.html', context)


@login_required
def saved_recipes(request):
    saved = request.user.profile.saved_recipes.all()  # або як у тебе реалізовано
    return render(request, 'recipes/saved_recipes.html', {'recipes': saved})

@login_required
def activity_log(request):
    return render(request, 'recipes/activity_log.html')

@login_required
def edit_profile(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        avatar = request.FILES.get('avatar')

        user = request.user
        user.username = username
        if avatar:
            user.profile_picture = avatar
        user.save()

        return redirect('profile')
    return redirect('profile')

@login_required
def edit_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)

    if recipe.author != request.user:
        return HttpResponseForbidden("Ви не маєте прав для редагування цього рецепту")

    if request.method == 'POST':
        form = RecipeForm(request.POST, request.FILES, instance=recipe)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = RecipeForm(instance=recipe)

    return render(request, 'recipes/edit_recipe.html', {'form': form})

@login_required
def delete_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk, author=request.user)
    if request.method == 'POST':
        recipe.delete()
        return redirect('profile')
    return render(request, 'recipes/confirm_delete.html', {'recipe': recipe})


@login_required
def delete_account(request):
    if request.method == 'POST':
        # Видаляємо всі рецепти користувача
        request.user.recipes.all().delete()

        # Видаляємо акаунт
        user = request.user
        logout(request)  # Спочатку виходимо
        user.delete()  # Потім видаляємо

        messages.success(request, 'Ваш акаунт було успішно видалено.')
        return redirect('recipe_list')

    return redirect('profile')

def search_categories(request):
    term = request.GET.get('term', '')
    categories = Category.objects.filter(name__icontains=term)[:10]  # Обмежуємо 10 результатами
    results = [{'id': c.id, 'name': c.name} for c in categories]
    return JsonResponse(results, safe=False)

@require_POST
@login_required
def save_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    request.user.saved_recipes.add(recipe)

    return render(request, 'recipes/partials/save_button.html', {
        'recipe': recipe,
        'is_saved': True,
    })

@require_POST
@login_required
def unsave_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    request.user.saved_recipes.remove(recipe)

    return render(request, 'recipes/partials/save_button.html', {
        'recipe': recipe,
        'is_saved': False,
    })

@require_POST
@login_required
def add_comment(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    text = request.POST.get('comment_text')
    if text:
        comment = Comment.objects.create(recipe=recipe, user=request.user, text=text)
    comments_html = render_to_string('recipes/partials/comments_list.html', {'recipe': recipe}, request=request)
    return HttpResponse(comments_html)

# Видалення коментаря
@require_POST
@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, user=request.user)
    recipe = comment.recipe
    comment.delete()
    comments_html = render_to_string('recipes/partials/comments_list.html', {'recipe': recipe}, request=request)
    return HttpResponse(comments_html)

# Редагування коментаря
@require_POST
@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    new_text = request.POST.get('comment_text')
    if new_text:
        comment.text = new_text
        comment.save()

        html = render_to_string('recipes/partials/comment_item.html', {
            'comment': comment,
            'user': request.user,  # 🛠️ Додаємо user в контекст обов'язково!
        }, request=request)

        return JsonResponse({'html': html})

    return JsonResponse({'error': 'Invalid data'}, status=400)

@require_POST
@login_required
def rate_recipe(request, pk):
    recipe = get_object_or_404(Recipe, pk=pk)
    data = json.loads(request.body)
    value = int(data.get('rating'))

    rating_obj, created = Rating.objects.update_or_create(
        user=request.user,
        recipe=recipe,
        defaults={'value': value}
    )

    # Оновлення середнього рейтингу
    ratings = recipe.ratings.all()
    avg = sum(r.value for r in ratings) / ratings.count()
    recipe.rating = round(avg, 1)
    recipe.ratings_count = ratings.count()
    recipe.save()

    return JsonResponse({'rating': recipe.rating})