FROM python:3.7

RUN apt-get update && apt-get -y install cron wkhtmltopdf
COPY docker/nanoforms/nanoforms-cron /etc/cron.d/nanoforms-cron
RUN chmod 0644 /etc/cron.d/nanoforms-cron
RUN crontab /etc/cron.d/nanoforms-cron
RUN touch /var/log/cron.log

ENV SELF_URL=http://entry
ENV CROMWELL_URL=http://cromwell:7338

WORKDIR /code
EXPOSE 8000
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .