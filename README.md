# Bitreport
Automated technical analysis reports for cryptocurrencies 🚀

This project was used to generate content for: https://twitter.com/Bitreport_org.

However, we decided to abandond it and open-source our code. Hopefully someone may find this helpfull.

## Setup
Everything is dockerized here, so all you need is docker. Just run `docker-compose up` and you're good to go.
Additonaly if you would like use pre-commit then:
- install [pre-commit](https://pre-commit.com) with `pip install pre-commit` or `brew install pre-commit`
- install required git hook `pre-commit install`

If you want you can run `pylint` over core but then you are obligated to fix errors 💁🏻‍♂️
```sh
pylint --output-format=colorized core/app/
```

## Deployment
We have CI/CD and stuff :tada:
