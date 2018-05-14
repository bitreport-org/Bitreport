# Use an official Python runtime as a parent image
FROM tailordev/pandas


# Set the working directory to /core
WORKDIR /core

COPY requirementsDocker.txt /tmp
WORKDIR /tmp

# Install any needed packages specified in requirements.txt
RUN apt-get install g++
RUN apt-get install gcc
RUN pip install -r requirementsDocker.txt

COPY src/ /core
WORKDIR /core

# Run core.py when the container launches
CMD ["gunicorn", "-w 4", "core:app"]

