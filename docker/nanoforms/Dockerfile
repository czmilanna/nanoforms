FROM python:3.7

RUN apt-get update && apt-get -y install wkhtmltopdf

ENV SELF_URL=http://entry
ENV CROMWELL_URL=http://cromwell:7338

WORKDIR /code
EXPOSE 8000
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .