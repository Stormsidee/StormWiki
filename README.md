# StormWiki (Python + Django)


# 📌 About
- My first web application on Django + Python + FastAPI, I am actively studying this framework, do not judge strictly <3



## ✈️ Quick Start
------------------------------------
> Frontend work on 8000 port

## Docker
```bash
docker-compose up -d --build
```

## Linux
```bash
chmod +x start.sh
./start.sh
```
------------------------------------
## 🛠 Technology stack
```bash
- Python 3.14
- Django
- FastAPI
- SQLite
- Docker, Docker-compose
```
------------------------------------
## ⚙️ How to use API
> API work on 7000 port (example 127.0.0.1:7000/tags/)

```bash
#GET /articles/ - This get all articles on site
#GET /tags/ - This get all used tags on site
#GET /users/ - This get all users
```
## /articles/create/ [POST]
```bash
{
  "title":"example",
  "content":"example content",
  "author_username":"testAPI",
  "tags":["test","FastAPI","example"]
}
```
## /articles/delete/ [POST]
```bash
{
  "article_id":5 <- here is any article ID
}
```
## /users/create/ [POST]
```bash
{
  "username":"example",
  "email":"example@example.com",
  "password":"example123"
}
```
------------------------------------
