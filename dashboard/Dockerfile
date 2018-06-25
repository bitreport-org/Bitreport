FROM ruby:2.5.1

# throw errors if Gemfile has been modified since Gemfile.lock
RUN bundle config --global frozen 1

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get update -qq && \
    apt-get install -y \
        build-essential \
        curl \
        gnuplot \
        graphicsmagick \
        libcairo2-dev \
        libpq-dev \
        nano \
        nodejs

WORKDIR /usr/src/app

COPY Gemfile Gemfile
COPY Gemfile.lock Gemfile.lock

RUN bundle install --no-deployment

COPY . .

RUN npm install

RUN cd /usr/share/fonts && \
    mkdir googlefonts && \
    cp -R /usr/src/app/vendor/assets/fonts/ googlefonts && \
    chmod -R --reference=truetype googlefonts && \
    fc-cache -fv

EXPOSE 3000
