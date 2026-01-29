# Використовуємо легкий Python образ
FROM python:3.11-slim

# Встановлюємо ffmpeg (критично для роботи з відео/аудіо)
RUN apt-get update && \
    apt-get install -y ffmpeg git && \
    rm -rf /var/lib/apt/lists/*

# Робоча папка
WORKDIR /app

# Копіюємо залежності та встановлюємо їх
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо код
COPY . .

# Створюємо папки для завантажень, щоб не було помилок
RUN mkdir -p downloads dubbed_files

# Запуск бота (замініть main.py на ваш файл запуску)
CMD ["python", "main.py"]