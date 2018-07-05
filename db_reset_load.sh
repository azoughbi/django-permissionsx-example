#!/bin/sh
rm ./db.sqlite
./manage.py syncdb --noinput
./manage.py loaddata ./fixtures/profiles.json
./manage.py loaddata ./fixtures/topics.json
./manage.py loaddata ./fixtures/content.json
