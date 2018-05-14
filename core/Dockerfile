FROM python:3.5-alpine

RUN apk add --update curl gcc g++ \
    && rm -rf /var/cache/apk/*

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

PIP_NO_BUILD_ISOLATION=false

RUN pip install Cython

RUN pip install bottle numpy pandas ta-lib

RUN pip install -r requirements.txt

COPY src/ /core
WORKDIR /core

# Run core.py when the container launches
CMD ["gunicorn", "-w 4", "core:app"]

