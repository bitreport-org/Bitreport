# Use an official Python runtime as a parent image
FROM python:3.6-alpine

# Set the working directory to /core
WORKDIR /core

COPY requirements.txt /

# Install any needed packages specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

COPY src/ /app
WORKDIR /app

# Run core.py when the container launches
CMD ["gunicorn", "-w 4", "main:core"]