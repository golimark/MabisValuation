#!/usr/bin/env bash

# install python and nginx
sudo apt update
sudo apt install python3 -y
sudo apt install nginx -y

# create virtual environment
sudo apt install python3.10-venv -y
python3 -m venv venv
source ./venv/bin/activate

# install dependences and run migrations
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate

# set up nginx
# check if config file exists
if [ -e "/etc/nginx/sites-available/MABiS" ]; then
    echo "MABiS Nginx config file already exists. Overwriting ...\n"
fi
sudo cp ./prod/MABiS /etc/nginx/sites-available/MABiS

if [ -e "/etc/nginx/sites-available/MABiS" ]; then
    echo "MABiS Nginx config symbolic link exits ...\n"
else
    sudo ln -s /etc/nginx/sites-available/MABiS /etc/nginx/sites-enabled/MABiS
fi
sudo systemctl restart nginx

# set gunicorn
pip install gunicorn
if [ -e "/etc/systemd/system/gunicorn.service" ]; then
    echo "MABiS gunicorn service config file already exists. Overwriting ...\n"
fi
sudo cp ./prod/gunicorn.service /etc/systemd/system/gunicorn.service
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
sudo systemctl daemon-reload


# add celery services
sudo cp ./prod/celery_worker.service /etc/systemd/system/celery_worker.service
sudo systemctl enable celery_worker
sudo systemctl start celery_worker


sudo cp ./prod/celery_beat.service /etc/systemd/system/celery_beat.service
sudo systemctl enable celery_beat
sudo systemctl start celery_beat
