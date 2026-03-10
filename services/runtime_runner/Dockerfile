FROM python:3.11-slim

WORKDIR /app

COPY . /app
RUN python -m pip install --no-cache-dir -e ".[web]"

EXPOSE 8770

CMD ["python", "-m", "scripts.runtime_runner_service"]
