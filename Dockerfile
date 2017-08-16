FROM python:2
ENV DEBIAN_FRONTEND noninteractive
RUN mkdir /code
RUN mkdir /log
WORKDIR /code
COPY ./requirements.txt /code/
COPY ./requirements /code/requirements
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash
RUN apt-get install nodejs
COPY . /code/
ADD ./log /log
ENV DEBIAN_FRONTEND teletype