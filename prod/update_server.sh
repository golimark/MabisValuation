#!/usr/bin/env bash

echo "Saving server state...\n"
git add .
read -p "Enter Commit Message: " commitMsg
git commit -am "$commitMsg"

echo "Pulling repository data...\n"
git fetch
git pull
echo "Confirm that there are no merge conflicts...\n"

source ./venv/bin/activate
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic

echo "Is database backup file present at ./prod?...\n"
read -p "Do you want to continue? (yes/no): " answer

if [[ $answer == [Yy]* ]]; then
sudo ./prod/update_server.sh
fi

sudo systemctl restart gunicorn
sudo systemctl restart celery_worker
sudo systemctl restart celery_beat
