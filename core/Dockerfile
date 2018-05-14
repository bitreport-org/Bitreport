# Use an official Python runtime as a parent image
<<<<<<< HEAD
FROM tailordev/pandas
=======
FROM python:3.6-alpine
>>>>>>> 84e43b94424d702cb600c3f97051509d57355926

# Set the working directory to /core
WORKDIR /core

COPY requirementsDocker.txt /tmp
WORKDIR /tmp

# Install any needed packages specified in requirements.txt
RUN pip install -r requirementsDocker.txt

COPY src/ /core
WORKDIR /core

# Run core.py when the container launches
<<<<<<< HEAD
CMD ["gunicorn", "-w 4", "core:app"]
=======
CMD ["gunicorn", "-w 4", "main:core"]
>>>>>>> 84e43b94424d702cb600c3f97051509d57355926
