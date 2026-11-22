FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Match the host user that owns ./static, so collectstatic can write into it.
ARG UID=1000
RUN useradd --uid "$UID" --create-home app
USER app

EXPOSE 8000
ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["gunicorn", "yint.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
