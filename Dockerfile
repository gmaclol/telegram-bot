FROM python:3.9-slim

# Imposta la directory di lavoro nel contenitore
WORKDIR /app

# Copia i file locali nel contenitore
COPY . .

# Installa le dipendenze
RUN pip install -r requirements.txt

# Esegui il bot
CMD ["python", "bot.py"]
