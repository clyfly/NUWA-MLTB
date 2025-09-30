FROM 5hojib/aeon:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

RUN uv venv
COPY requirements.txt .
RUN uv pip install --no-cache-dir -r requirements.txt

COPY . .
CMD ["bash", "start.sh"]