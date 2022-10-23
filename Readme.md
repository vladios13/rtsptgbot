<h1 align="center">RTSPtgbot</h1>


## О боте ##
С помощью этого бота вы можете получить скриншот, либо GIF-запись с вашей камеры, посредством RTSP-потока, а также пинговать ip-адрес.

## Технологии ##

В данном проекте были использованы следующие инструменты:

- [Aiogram](https://github.com/aiogram/aiogram)
- [Python 3.8](https://www.python.org/)
- [ffmpeg-python](https://github.com/kkroening/ffmpeg-python)


## Запуск бота ##

Перед первым запуском, требуется переименовать "config-example.py", в "config.py". 
Заполнить необходимые данные, следуя комментариям в коде, а также установить все требуемые зависимости.

Клонируем репозиторий: 
```bash
git clone https://github.com/vladios13/rtsptgbot.git
```

Установка зависимостей:
```bash
pip3 install -r requirements.txt
```

Редактируем config.py
```python
TOKEN = ''  # токен Telegram бота

CAM_1 = "" # rtsp данные камеры

RTSP_PING = "" # IP роутера
```

------------
&#xa0;

### vladios13
[Блог vladios13](https://blog.vladios13.com/rtsptgbot/)

[Telegram](https://t.me/vladios13blog)

Для пожертвований:
[Yoomoney](https://yoomoney.ru/to/410011568729023 "Yoomoney")
