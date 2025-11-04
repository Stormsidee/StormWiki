from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Article, Tag
from .forms import ArticleForm

def article_list(request):
    """Список статей с поиском и фильтрацией"""
    articles = Article.objects.filter(is_published=True)
    
    query = request.GET.get('q')
    if query:
        articles = articles.filter(
            Q(title__icontains=query) | 
            Q(content__icontains=query) |
            Q(tags__name__icontains=query)
        ).distinct()
    
    tag_filter = request.GET.get('tag')
    if tag_filter:
        articles = articles.filter(tags__name=tag_filter)
    
    paginator = Paginator(articles, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
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
    article = get_object_or_404(Article, pk=pk, is_published=False)
    
    similar_articles = Article.objects.filter(
        tags__in=article.tags.all(),
        is_published=True
    ).exclude(pk=article.pk).distinct()[:5]
    
    context = {
        'article': article,
        'similar_articles': similar_articles,
    }
    
    return render(request, 'article_detail.html', context)

# ВРЕМЕННО УБИРАЕМ @login_required
def article_create(request):
    """Создание новой статьи"""
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            # Временное решение - берем первого пользователя
            article.author = User.objects.first()
            article.save()
            form.save_m2m()  # Сохраняем теги
            
            messages.success(request, f'Статья "{article.title}" успешно создана!')
            return redirect('article_detail', pk=article.pk)
    else:
        form = ArticleForm()
    
    context = {
        'form': form,
        'title': 'Создание статьи',
    }
    
    return render(request, 'article_form.html', context)

# ВРЕМЕННО УБИРАЕМ @login_required  
def article_edit(request, pk):
    """Редактирование статьи"""
    article = get_object_or_404(Article, pk=pk)
    
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

# ВРЕМЕННО УБИРАЕМ @login_required
def article_delete(request, pk):
    """Удаление статьи"""
    article = get_object_or_404(Article, pk=pk)
    
    if request.method == 'POST':
        title = article.title
        article.delete()
        messages.success(request, f'Статья "{title}" успешно удалена!')
        return redirect('article_list')
    
    context = {
        'article': article,
    }
    
    return render(request, 'article_confirm_delete.html', context)

# ВРЕМЕННО КОММЕНТИРУЕМ ЭТОТ VIEW
# @login_required
# def my_articles(request):
#     """Список статей текущего пользователя"""
#     articles = Article.objects.filter(author=request.user)
#     ...