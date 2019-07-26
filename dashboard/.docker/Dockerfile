FROM registry.gitlab.com/bitreport/bitreport/ruby2.6-dashboard

WORKDIR /usr/src/app

COPY package.json yarn.lock ./

RUN yarn install

COPY . .

RUN cd /usr/share/fonts && \
    mkdir googlefonts && \
    cp -R /usr/src/app/vendor/assets/fonts/ googlefonts && \
    chmod -R --reference=truetype googlefonts && \
    fc-cache -fv

COPY .docker/development-entrypoint.sh /
RUN chmod +x /development-entrypoint.sh
ENTRYPOINT ["/development-entrypoint.sh"]

EXPOSE 3000
