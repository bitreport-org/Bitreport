FROM registry.gitlab.com/bitreport/bitreport/python3.7-core

# Install requirements
RUN pip install --upgrade pip
RUN pip install -U pyopenssl

# To cache TA-lib build
RUN pip install numpy==1.16.3
RUN pip install TA-Lib==0.4.17

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app
COPY . .
