FROM python:3.13-slim

WORKDIR /app

# Install git (and clean apt cache to keep image small)
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Install python pip requirements
COPY requirements.txt /app
RUN pip install -r requirements.txt

# Copy project files
COPY . /app

# Run in unbuffered mode for stdout
ENTRYPOINT ["python3", "-u"]
CMD ["bot.py"]
