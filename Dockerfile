# Pull base image
FROM python:3.8

# This will add scripts to the path of the running container
# ENV PATH="/scripts:${PATH}"

# Set environment variables
# PYTHONUNBUFFERED ensures our console output looks familiar 
# and is not buffered by Docker
ENV PYTHONUNBUFFERED 1 
# PYTHONDONTWRITEBYTECODE means Python won't try to write .pyc files
ENV PYTHONDONTWRITEBYTECODE 1
ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive 

# Create and set working directory
# set the WORKDIR to /code. This means the working directory is 
# located at /code so in the future to run any commands like 
# manage.py we can just use WORKDIR rather than need to remember 
# where exactly on Docker our code is actually located.
RUN mkdir /code
WORKDIR /code

# install environment dependencies
RUN pip3 install --upgrade pip 
RUN pip3 install pipenv

COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Using below command we can run docker as non 
# root user, which is a good practice
# RUN adduser -D user
