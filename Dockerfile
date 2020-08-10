FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
COPY config/requirements.txt /code/
RUN pip3 install -r requirements.txt
COPY . /code/