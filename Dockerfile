ARG PORT=443
FROM cypress/browsers:latest

# Always update package index before installing packages
RUN apt-get update && apt-get install -y python3

RUN echo $(python3 -m site --user-base)

COPY requirements.txt .

ENV PATH /home/root/.local/bin:${PATH}

RUN apt-get update && apt-get install -y python3-pip && pip install -r requirements.txt && pip install huey

COPY . .

ENTRYPOINT ["supervisord", "-c", "supervisord.conf"]