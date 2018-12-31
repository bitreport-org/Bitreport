FROM python:3.6.7

# TA-lib dependencies
RUN curl -s -L http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz | tar -xz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib

# Some crazy modules from python
RUN pip install Cython
RUN pip install numpy
RUN pip install pandas
RUN pip install ta-lib
RUN pip install -U pyopenssl

# Install requirements
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app
COPY . .

EXPOSE 80

# Run core.py when the container launches
CMD ["gunicorn", "-b 0.0.0.0:80", "-w 1", "core:app"]
