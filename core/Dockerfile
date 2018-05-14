# Use an official Python runtime as a parent image
FROM python:3.5-alpine


# Set the working directory to /core
WORKDIR /core

COPY requirementsDocker.txt /tmp
WORKDIR /tmp

# Install any needed packages specified in requirements.txt
RUN apk add --update curl gcc g++ && rm -rf /var/cache/apk/*

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

RUN pip install bottle numpy cython pandas ta-lib

RUN pip install -r requirementsDocker.txt

COPY src/ /core
WORKDIR /core

# Run core.py when the container launches
CMD ["gunicorn", "-w 4", "core:app"]

