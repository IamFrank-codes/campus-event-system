FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY . .
RUN for d in user-service event-service booking-service notification-service review-services; do pip install --no-cache-dir -r "$d/requirements.txt"; done
RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser
EXPOSE 8001 8002 8003 8004 8005
