########################################
# 1) Build the frontend                #
########################################
FROM node:23-alpine AS frontend-builder

RUN apk update \
 && apk upgrade --no-cache \
 && apk add --no-cache tini

WORKDIR /app/frontend
COPY frontend/team_sync_front/package*.json ./
RUN npm ci
COPY frontend/team_sync_front/ ./
RUN npm run build


########################################
# 2) Build the backend on Python 3.11  #
########################################
FROM python:3.11-slim

LABEL maintainer="TeamSync" \
      description="TeamSync application"

# system deps & cleanup
RUN apt-get update \
 && apt-get upgrade -y \
 && apt-get install -y --no-install-recommends \
      curl build-essential gfortran python3-dev libatlas-base-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install Python deps (this will now pick up wheels for numpy/pandas)
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -r requirements.txt

# copy app + static
COPY backend/ ./
COPY --from=frontend-builder /app/frontend/dist ./static

# drop privileges
RUN groupadd -r teamsync \
 && useradd -r -g teamsync -d /app -s /bin/bash teamsync \
 && chown -R teamsync:teamsync /app

USER teamsync

EXPOSE 5000

ENV REDIS_URL=redis://redis:6379/0 \
    FLASK_ENV=development \
    FLASK_DEBUG=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]