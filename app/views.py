from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Article, Tag
from .forms import ArticleForm, CustomUserCreationForm, CustomAuthenticationForm

# Аутентификация
def register_view(request):
    if request.user.is_authenticated:
        return redirect('article_list')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Добро пожаловать, {user.username}!')
            return redirect('article_list')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('article_list')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'С возвращением, {username}!')
                next_url = request.GET.get('next', 'article_list')
                return redirect(next_url)
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.info(request, 'Вы успешно вышли из системы.')
    return redirect('article_list')

# Основные views (ТЕПЕРЬ С АВТОРИЗАЦИЕЙ)
@login_required
def article_create(request):
    """Создание новой статьи"""
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            form.save_m2m()
            
            messages.success(request, f'Статья "{article.title}" успешно создана!')
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm()
    
    context = {
        'form': form,
        'title': 'Создание статьи',
    }
    
    return render(request, 'article_form.html', context)

@login_required
def article_edit(request, pk):
    """Редактирование статьи - ТОЛЬКО СВОИХ СТАТЕЙ"""
    article = get_object_or_404(Article, pk=pk, author=request.user)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save()
            messages.success(request, f'Статья "{article.title}" успешно обновлена!')
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    
    context = {
        'form': form,
        'title': 'Редактирование статьи',
        'article': article,
    }
    
    return render(request, 'article_form.html', context)

@login_required
def article_delete(request, pk):
    """Удаление статьи - ТОЛЬКО СВОИХ СТАТЕЙ"""
    article = get_object_or_404(Article, pk=pk, author=request.user)
    
    if request.method == 'POST':
        title = article.title
        article.delete()
        messages.success(request, f'Статья "{title}" успешно удалена!')
        return redirect('article_list')
    
    context = {
        'article': article,
    }
    
    return render(request, 'article_confirm_delete.html', context)

@login_required
def my_articles(request):
    """Список статей текущего пользователя"""
    articles = Article.objects.filter(author=request.user)
    
    query = request.GET.get('q')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query)
        )
    
    status_filter = request.GET.get('status')
    if status_filter == 'published':
        articles = articles.filter(is_published=True)
    elif status_filter == 'draft':
        articles = articles.filter(is_published=False)
    
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'articles': page_obj,
        'page_obj': page_obj,
        'query': query,
        'status_filter': status_filter,
    }
    
    return render(request, 'my_articles.html', context)

# Эти views остаются публичными
def article_list(request):
    """Список ВСЕХ опубликованных статей с поиском и фильтрацией"""
    # Берем ВСЕ опубликованные статьи, независимо от автора
    articles = Article.objects.filter(is_published=True).select_related('author').prefetch_related('tags')
    
    # Поиск
    query = request.GET.get('q')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    # Фильтрация по тегу
    tag_filter = request.GET.get('tag')
    if tag_filter:
        articles = articles.filter(tags__name=tag_filter)
    
    # Сортировка по дате обновления (новые сверху)
    articles = articles.order_by('-updated_at')
    
    # Пагинация
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Все теги для фильтра
    all_tags = Tag.objects.all()
    
    context = {
        'articles': page_obj,
        'page_obj': page_obj,
        'all_tags': all_tags,
        'query': query,
        'tag_filter': tag_filter,
    }
    
    return render(request, 'articles.html', context)

def article_detail(request, pk):
    """Детальная страница статьи"""
    try:
        article = Article.objects.get(pk=pk)
        
        # Проверяем права доступа
        is_author = request.user.is_authenticated and article.author == request.user
        can_edit = is_author
        
        # Если статья не опубликована и пользователь не автор - 404
        if not article.is_published and not is_author:
            raise Article.DoesNotExist
            
    except Article.DoesNotExist:
        messages.error(request, 'Статья не найдена или у вас нет прав для ее просмотра.')
        return redirect('article_list')
    
    # Похожие статьи (только опубликованные)
    similar_articles = Article.objects.filter(
        tags__in=article.tags.all(),
        is_published=True
    ).exclude(pk=article.pk).distinct()[:5]
    
    context = {
        'article': article,
        'similar_articles': similar_articles,
        'is_author': is_author,
        'can_edit': can_edit,
    }
    
    return render(request, 'article_detail.html', context)