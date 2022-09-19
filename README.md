# Yatube
Скромный автор Izrekatel представляет свой проект.

## Проект приложения Yatube

Объединенный проект учебного процесса Яндекс.Практикум - Yatube
Включает в себя сайт Yatube, API к нему. На сайте возможна регистрация,
публикация постов, комментариев к ним и подписок на авторов.
API позволяет осуществлять CRUD команды.
Может управлять постами, группами, комментариями, подписками,
регистрацией на сайте.

### Технологии:

Написан на Python, c использованием Django, дополненный djoser и
обрабатывающий запросы через requests.


### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:

```
git clone https://github.com/Izrekatel/Yatube.git
```
Войти в папку репозитария
```
cd Yatube
```

Cоздать виртуальное окружение:

```
python3.7 -m venv venv
```
Активировть виртульное окружение
```
source venv/bin/activate
or
source venv/scripts/activate
```
Обновить pip
```
python -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python yatube/manage.py migrate
```

Запустить проект:

```
python yatube/manage.py runserver
```

### Ccылка на документацию:

После запуска сервера не забудьте ознакомиться с документацией:

http://127.0.0.1:8000/redoc/

### Примеры запросов API:

http://127.0.0.1:8000/api/v1/posts/{id}/

http://127.0.0.1:8000/api/v1/posts/{post_id}/comments/{id}/

http://127.0.0.1:8000/api/v1/groups/{id}/

http://127.0.0.1:8000/api/v1/follow/

http://127.0.0.1:8000/api/v1/jwt/...