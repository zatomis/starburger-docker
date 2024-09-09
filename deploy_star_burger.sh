#!/bin/bash
set -e
git pull
echo "Сегодня " `date`

docker-compose -f docker-compose.prod.yaml exec django-web bash -c "pip3 install -r requirements.txt &&
    python3 manage.py collectstatic --noinput &&
    python3 manage.py migrate --noinput"

docker-compose -f docker-compose.prod.yaml up -d node-web
docker-compose -f docker-compose.prod.yaml restart django-web
docker-compose -f docker-compose.prod.yaml restart nginx
hash=$(git rev-parse HEAD)

clear
echo 'Выполняется обновление данных'
FILE=.env
if test -f "$FILE"; then
	source .env
	git_id="$(git rev-parse --verify HEAD)"
	user="$(whoami)"
	echo $ROLLBAR_TOKEN_KEY
	curl --request POST \
	     --url https://api.rollbar.com/api/1/deploy \
	     --header 'X-Rollbar-Access-Token: '$ROLLBAR_TOKEN_KEY \
	     --header 'accept: application/json' \
	     --header 'content-type: application/json' \
	     --data '
	{
	  "rollbar_username": "'user'",
	  "environment": "PyCharm",
	  "revision": "1",
	  "local_username": "'user'",
	  "comment": "Comment git: '$git_id'",
	  "status": "succeeded"
	}'
	echo "Деплой успешно произведен"
else
	echo -n "Отсутствует основной файл конфигурации .env"$'\n'$FILE$'\n'"Необходимo прочесть Readme"
fi
