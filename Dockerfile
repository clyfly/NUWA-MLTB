FROM 5hojib/aeon:latest

WORKDIR /app
RUN chmod 777 /app

RUN uv venv
COPY requirements.txt .
RUN uv pip install --no-cache-dir -r requirements.txt

COPY . .

# Health check for Heroku/container orchestration
HEALTHCHECK --interval=60s --timeout=10s --start-period=120s --retries=3 \
    CMD curl -f http://localhost:${PORT:-80}/health || exit 1

CMD ["bash", "start.sh"]
