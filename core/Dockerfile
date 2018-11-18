FROM python:3.6.7

RUN mkdir app
WORKDIR /app
ADD . /app

# TA-lib dependencies
RUN wget "http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz"
RUN tar xf ta-lib-0.4.0-src.tar.gz
WORKDIR ta-lib
RUN ./configure --prefix=/usr
RUN make
RUN make install

WORKDIR /tmp

# Some crazy modules from python
RUN pip install Cython
RUN pip install numpy
RUN pip install pandas
RUN pip install ta-lib
RUN pip install -U pyopenssl

# Install requirements
COPY requirements.txt /tmp
WORKDIR /tmp
RUN pip install -r requirements.txt

WORKDIR /app

EXPOSE 80

# Run core.py when the container launches
# CMD ["gunicorn", "-b 0.0.0.0:80", "-w 4", "core:app"]
CMD ["python", "run.py"]
