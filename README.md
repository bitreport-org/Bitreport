[![CircleCI](https://circleci.com/gh/nuclearpinguin/Bitreport/tree/master.svg?style=svg&circle-token=e676d0a74df9747c7251c49b88072ce4e8fe36ef)](https://circleci.com/gh/nuclearpinguin/Bitreport/tree/master)

# Bitreport
Daily bitfinex report

## Setup
Everything is dockerized here, so all you need is docker. Just run `docker-compose up` and you're good to go

## Deployment
Right now we use docker machine, which is like a million years old technology and is causing much trouble.

To do a deployment you must have all `docker-machine` keys on your computers (How do you get them? No one really knows ¯\\\_(ツ)\_/¯) and execute the following from the project's root directory:
```sh
$ eval $(docker-machine env bitreport-prod) # This setups docker-machine. Watch out as everything you do now will happen on production
$ docker-compose -f docker-compose.production.yml down # Since we're going to build all images on server we're going to need some resources. We free them by killing everything (yeah, great idea :D)
$ docker-compose -f docker-compose.production.yml up -d --build # Now start all services again and ask them to rebuild
```
If nothing died in the process your app should now be running in the latest version (or more specifically, the one you had on your local computer).

Also don't forget to run any migrations:
```sh
$ docker-compose -f docker-compose.production.yml run --rm dashboard bundle exec rake db:migrate:with_data
```

Now it's time to close the terminal session in order not to mess up anything :flushed:
