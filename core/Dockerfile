FROM python:3.5-alpine

RUN apk add --update curl gcc g++ \
    && rm -rf /var/cache/apk/*

RUN ln -s /usr/include/locale.h /usr/include/xlocale.h

RUN pip install cython

RUN pip install bottle numpy pandas ta-lib

CMD tail -f /dev/null

RUN pip install -r requirements.txt

COPY src/ /core
WORKDIR /core

# Run core.py when the container launches
CMD ["gunicorn", "-w 4", "core:app"]

