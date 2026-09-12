FROM python:3.12-slim

WORKDIR /app

COPY apps/api/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY apps/api/app ./app
COPY apps/api/docker-entrypoint.sh ./docker-entrypoint.sh
COPY seed ./seed

RUN chmod +x ./docker-entrypoint.sh

ENV PYTHONPATH=/app
EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
