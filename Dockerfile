FROM python:3.11-slim

WORKDIR /app

# Variables d'environnement
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Installer dépendances
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . /app

# Créer répertoires nécessaires
RUN mkdir -p /app/logs /app/data/index /app/data/corpus

# Port
EXPOSE 8000

# Commande de démarrage
CMD ["python", "app/main.py"]
