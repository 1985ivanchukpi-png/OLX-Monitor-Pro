FROM python:3.10-slim
WORKDIR /app
RUN pip install python-telegram-bot==13.15 requests beautifulsoup4
COPY . .
CMD ["python", "bot.py"]
