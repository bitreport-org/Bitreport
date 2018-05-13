# Use an official Python runtime as a parent image
FROM python:3.6-alpine

# Set the working directory to /core
WORKDIR /core

COPY requirements.txt /tmp
WORKDIR /tmp

# Install any needed packages specified in requirements.txt
RUN pip install -U setuptools
RUN python -m pip install --upgrade pip
RUN pip install -t packages -r requirements.txt

COPY src/ /core
WORKDIR /core

# Run core.py when the container launches
CMD ["gunicorn", "-w 4", "main:core"]