#! /bin/bash
set -e

: ${APP_PATH:="/usr/src/app"}
: ${APP_TEMP_PATH:="$APP_PATH/tmp"}
: ${APP_SETUP_LOCK:="$APP_TEMP_PATH/setup.lock"}
: ${APP_SETUP_WAIT:="10"}

function lock_setup { mkdir -p $APP_TEMP_PATH && touch $APP_SETUP_LOCK; }
function unlock_setup { rm -rf $APP_SETUP_LOCK; }
function wait_setup { echo "Waiting for app setup to finish..."; sleep $APP_SETUP_WAIT; }

trap unlock_setup HUP INT QUIT KILL TERM EXIT

if [ -z "$1" ]; then set -- rails server -p 3000 -b 0.0.0.0 "$@"; fi

bundle check || bundle install

if [[ "$1" = "rails" || "$1" = "sidekiq" ]]
then
  while [ -f $APP_SETUP_LOCK ]; do wait_setup; done

  lock_setup

  echo "Preparing database"

  bundle exec rails db:migrate || bundle exec rails db:setup

  unlock_setup

  if [[ "$2" = "s" || "$2" = "server" ]]; then rm -rf /usr/src/app/tmp/pids/server.pid; fi
fi

if [[ "$1" = "bundle" ]]
then
  exec "$@"
else
  echo "Starting $1. It should be ready in a few seconds"
  exec bundle exec "$@"
fi
