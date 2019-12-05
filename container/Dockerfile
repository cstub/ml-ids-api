FROM python:3.7.5-slim

RUN useradd -ms /bin/bash app

WORKDIR /home/app

COPY container/requirements.txt requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY config.py wsgi.py entrypoint.sh ./
COPY ml_ids_api ml_ids_api

RUN chmod +x entrypoint.sh

RUN chown -R app:app ./
USER app

EXPOSE 5000
ENTRYPOINT ["./entrypoint.sh"]