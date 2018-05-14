FROM python:3.5-alpine

RUN apk add --update curl gcc g++ \
    && rm -rf /var/cache/apk/*
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

# Talib
ADD http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz /core
RUN tar -zxvf ta-lib-0.4.0-src.tar.gz
RUN cd/ta-lib
RUN ./configure --prefix=/usr
RUN make
RUN cd ..

RUN PIP_NO_BUILD_ISOLATION=false pip install Cython
RUN PIP_NO_BUILD_ISOLATION=false pip install numpy
RUN PIP_NO_BUILD_ISOLATION=false pip install pandas
RUN PIP_NO_BUILD_ISOLATION=false pip install ta-lib

COPY requirements.txt /tmp
WORKDIR /tmp

RUN PIP_NO_BUILD_ISOLATION=false pip install -r requirements.txt

COPY src/ /core
WORKDIR /core

# Run core.py when the container launches
CMD ["gunicorn", "-w 4", "core:app"]

