FROM registry.gitlab.com/bitreport/bitreport/ruby2.6-dashboard

ENV RAILS_ENV production
ENV RAILS_ROOT /usr/src/app

WORKDIR $RAILS_ROOT

COPY Gemfile Gemfile.lock ./

RUN bundle install --jobs 20 --retry 5 --without development test

COPY package.json yarn.lock ./

RUN yarn install

COPY . .

RUN cd /usr/share/fonts && \
    mkdir googlefonts && \
    cp -R /usr/src/app/vendor/assets/fonts/ googlefonts && \
    chmod -R --reference=truetype googlefonts && \
    fc-cache -fv

# That is not working because volume is not yet mounted
# RUN bundle exec rake assets:precompile

EXPOSE 3000

CMD ["bundle", "exec", "puma", "-C", "config/puma.rb"]
