FROM cypress/browsers:latest

ENV PORT=443
ENV PATH=/root/.local/bin:$PATH

# Install Python, pip, and supervisor
RUN apt-get update && apt-get install -y python3 python3-pip supervisor \
    && python3 -m pip install --upgrade pip

# Copy requirements and install
COPY requirements.txt .
RUN python3 -m pip install --user -r requirements.txt \
    && python3 -m pip install --user huey

# Copy app
COPY . .

# Run supervisord
ENTRYPOINT ["supervisord", "-c", "supervisord.conf"]
