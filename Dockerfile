FROM python:3.14.0

RUN apt-get update && apt-get install -y \
    postgresql-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY require.txt .

RUN pip install --no-cache-dir -r require.txt

COPY . .

RUN mkdir -p staticfiles media

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["sh", "-c", "python manage.py migrate && python manage.py collectstatic --noinput && gunicorn your_project.wsgi:application --bind 0.0.0.0:8000 --workers 3"]