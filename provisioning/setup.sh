#!/usr/bin/env bash

if [[ -L "${BASH_SOURCE[0]}" ]]
then
  DIR="$( cd "$( dirname $( readlink "${BASH_SOURCE[0]}" ) )" && pwd )"
else
  DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
fi

cd $DIR

cp $DIR/etc/systemd/system/gitconsensusworker.service /etc/systemd/system/gitconsensusworker.service
cp $DIR/etc/gitconsensus/celery /etc/gitconsensus/celery


adduser --gecos "" --disabled-login gitconsensus

echo "d /var/run/celery 0755 celery celery -" >> /etc/tmpfiles.d/celery.conf
echo "d /var/log/celery 0755 celery celery - " >> /etc/tmpfiles.d/celery.conf

