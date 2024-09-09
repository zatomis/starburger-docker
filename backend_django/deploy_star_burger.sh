#!/bin/bash -e
clear
echo "Сегодня " `date`
echo 'Выполняется обновление данных'
git pull
echo 'Создание среды окружения Python'
python3 -m venv venv
source venv/bin/activate
echo 'Установка зависимостей '
pip install -r requirements.txt
pip install django-extensions
pip install rollbar
clear
echo 'Установка NodeJS '
npm ci --dev
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"
echo 'Сбор статики '
python3 manage.py collectstatic --noinput
echo 'Выполнение миграции '
python3 manage.py migrate
clear
echo 'Перезапуск служб '

FILE=/etc/systemd/system/burger-shop-devman.service
if test -f "$FILE"; then
	sudo systemctl restart burger-shop-devman.service
else
	echo -n "Отсутствует файл для работы сервиса"$'\n'$FILE$'\n'"Необходимо создать. Используйте Readme проекта"
fi

FILE1=/etc/systemd/system/nginx.service
if test -f "$FILE1"; then
	sudo systemctl reload nginx.service
else
	clear
	echo -n "Отсутствует NGINX сервис"$'\n'$FILE1$'\n'"Необходимо установить"
fi

FILE=/opt/star-burger/.env
if test -f "$FILE"; then
	cd /opt/star-burger
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
else
	echo -n "Отсутствует основной файл конфигурации .env"$'\n'$FILE$'\n'"Необходимo прочесть Readme"
fi

echo -n "Ok..."
