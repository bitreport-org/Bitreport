FROM python:3.7

# TA-lib dependencies
RUN curl -s -L http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz | tar -xz && \
    cd ta-lib && \
    ./configure --prefix=/usr && \
    make && \
    make install && \
    cd .. && \
    rm -rf ta-lib

# Install requirements
RUN pip install --upgrade pip
RUN pip install -U pyopenssl
RUN pip install numpy
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app
COPY . .
