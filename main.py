import os
import django
from asgiref.sync import sync_to_async

os.environ.setdefault('DJANGO_SETTINGS_MODULE','wiki.settings')
django.setup()

from fastapi import FastAPI, HTTPException
from django.contrib.auth.models import User
from app.models import Article, Tag  
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

app = FastAPI(
    title="API",
    description="",
    version="1.0"
)

class ArticleCreate(BaseModel):
    title: str
    content: str
    author_username: str 
    tag_names: Optional[List[str]] = []
    is_published: bool = True

def serialize_article(article):
    return {
        "id": article.id,
        "title": article.title,
        "content": article.content,
        "author": {
            "id": article.author.id,
            "username": article.author.username,
            "email": article.author.email
        },
        "tags": [
            {"id": tag.id, "name": tag.name} 
            for tag in article.tags.all()
        ],
        "created_at": article.created_at.isoformat(),
        "updated_at": article.updated_at.isoformat(),
        "is_published": article.is_published
    }


@app.get('/')
def root():
    return {"message":"API is running"}

@app.get('/articles/')
def get_articles():
    articles = list(Article.objects.all().values(
        'id', 'title', 'author__username', 'created_at'
    ))
    return {"articles": articles}


@app.post('/articles/create')
def create_article(article_data: ArticleCreate):
    try:
        try:
            author = User.objects.get(username=article_data.author_username, is_active=True)
        except User.DoesNotExist:
            available_users = list(User.objects.filter(is_active=True).values_list('username', flat=True))
            raise HTTPException(
                status_code=404, 
                detail=f"Author '{article_data.author_username}' not found. Available users: {', '.join(available_users)}"
            )
        
        article = Article(
            title=article_data.title,
            content=article_data.content,
            author=author,
            is_published=article_data.is_published
        )
        article.save()
        
        if article_data.tag_names:
            tags_to_add = []
            for tag_name in article_data.tag_names:
                tag, created = Tag.objects.get_or_create(
                    name=tag_name.strip(), 
                    defaults={'name': tag_name.strip()}
                )
                tags_to_add.append(tag)
            
            article.tags.set(tags_to_add)
        
        return serialize_article(article)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    
@app.get('/users/')
def get_users():
    users = list(User.objects.filter(is_active=True).values('id', 'username', 'email'))
    return {"users": users}

@app.get('/tags/')
def get_tags():
    tags = list(Tag.objects.all().values('id', 'name'))
    return {"tags": tags}