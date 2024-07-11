# Указываем базовый образ Python версии 3.10
FROM python:3.10-slim
# Устанавливаем рабочую директорию внутри контейнера как /app
WORKDIR /app/
# добавляем в контейнер в директорию app наше приложение и зависимости.
COPY server /app/server
COPY client /app/client
COPY run.py /app/
COPY requirements.txt /app/
# Установка зависимостей
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt
# Указываем переменные окружения для подключения к базе данных PostgreSQL
ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=1122
ENV POSTGRES_DB=db
# Запускаем приложение
CMD ["python", "run.py"]
