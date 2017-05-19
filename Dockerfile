FROM python:2
ENV DEBIAN_FRONTEND noninteractive
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y --no-install-recommends apt-utils
RUN curl -sL https://deb.nodesource.com/setup_6.x | bash
RUN apt-get install nodejs
ADD . /code/
ENV DEBIAN_FRONTEND teletype