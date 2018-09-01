FROM ruby:2.5.1

# throw errors if Gemfile has been modified since Gemfile.lock
# RUN bundle config --global frozen 1

RUN curl -sL https://deb.nodesource.com/setup_8.x | bash -
RUN apt-get update -qq && \
    apt-get install -y \
        build-essential \
        curl \
        gnuplot \
        libcairo2-dev \
        libpq-dev \
        nano \
        nodejs \
        libxml2-dev \
        libfftw3-dev \
        libmagickwand-dev \
        libopenexr-dev \
        liborc-0.4-0 \
        gobject-introspection \
        libgsf-1-dev \
        libglib2.0-dev \
        liborc-0.4-dev \
        libpng-dev \
        libpango1.0-dev \
        automake \
        libtool \
        swig \
        gtk-doc-tools

RUN git clone https://github.com/jcupitt/libvips.git && \
    cd libvips && \
    ./autogen.sh && \
    make && \
    make install && \
    echo "export VIPSHOME=/usr/local; \
         export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:$VIPSHOME/lib; \
         export PATH=$PATH:$VIPSHOME/bin; \
         export PKG_CONFIG_PATH=$PKG_CONFIG_PATH:$VIPSHOME/lib/pkgconfig; \
         export MANPATH=$MANPATH:$VIPSHOME/man; \
         export PYTHONPATH=$VIPSHOME/lib/python2.7/site-packages;" > ~/.bashrc && \
     cd ~ && \
     rm -rf libvips && \
     ldconfig

WORKDIR /usr/src/app

COPY . .

RUN npm install

RUN cd /usr/share/fonts && \
    mkdir googlefonts && \
    cp -R /usr/src/app/vendor/assets/fonts/ googlefonts && \
    chmod -R --reference=truetype googlefonts && \
    fc-cache -fv

COPY ./development-entrypoint.sh /
RUN chmod +x /development-entrypoint.sh
ENTRYPOINT ["/development-entrypoint.sh"]

EXPOSE 3000
