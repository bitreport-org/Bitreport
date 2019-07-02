#!/bin/bash

(
  ssh $SSH_USERNAME@$SSH_HOSTNAME -o StrictHostKeyChecking=no <<-EOF
    cd Bitreport
    git pull
    docker-compose pull
    docker-compose stop
    docker-compose rm -f
    ddocker-compose -f docker-compose.production.yml up -d
EOF
)
