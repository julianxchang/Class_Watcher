
FROM debian:stable-slim

ENV VENV_PATH=/opt/venv
ENV PATH="$VENV_PATH/bin:$PATH"

RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-venv \
        python3-pip \
        supervisor \
        curl \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv $VENV_PATH && \
    pip install --upgrade pip setuptools wheel

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

CMD ["supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
