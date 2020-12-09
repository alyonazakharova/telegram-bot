# Telegram-Bot @StatInfoBot COVID-19 Statistic


## Команда:

- Захарова Алена

- Федоров Данила

- Селезнев Вячеслав

- Климчук Даниил

- Группа 3530904/80104


## Проблема:

- Задача нашего бота снабжать статистикой пользователя. Для этого у него есть возможность ввести страну или отправить свою локацию для получения статистики по коронавирусной инфекции. Бот называется @StatInfoTestBot


## Требования:

![requirement](/docs/Screenshots/requirement.JPG)


## Диаграммы:

- Level 1: A System Context diagram provides a starting point, showing how the software system in scope fits into the world around it.

![diagram1](/docs/Screenshots/diagram1.JPG)

- Level 2: A Container diagram zooms into the software system in scope, showing the high-level technical building blocks.

![diagram2](/docs/Screenshots/diagram2.JPG)


## Результаты работы:

- Начало работы:

![diagram2](/docs/Screenshots/start.JPG)

- Получение статистики:

![diagram2](/docs/Screenshots/statistic.JPG)

- Отправка геопозиции:

![diagram2](/docs/Screenshots/location.JPG)

- Статистика по стране:

![diagram2](/docs/Screenshots/country.JPG)

- Команда:

![diagram2](/docs/Screenshots/contacts.JPG)


## Тестирование:

- Скрипт tests.py содержит тесты, написанные с использованием библиотеки для тестирования tgintegration и pyrogram — фреймворка, который действует как полноценный клиент Telegram на основе MTProto.
Тестируется все доступные команды. Проверяется, что в ответ от бота пользователь получает нужное количество сообщений(одно либо два в случае команды /start), а также что сообщение содержит нужную фразу.
Тестовые сообщения отправляются с аккаунта, api_id и api_hash которого указаны в конфигурационном файле (из API Development tools на https://my.telegram.org/)


## Сборка:

- 1.	Устанавливаем зависимости
		$ pip install -r requirements.txt
		(предполагается, что установлен интерпретатор python 3.8, а также пакетный менеджер pip)
		
- 2.	Запускаем программу
		$ python app.py
		
- 3.	Запускаем тесты
		$ python tests.py


## Вывод:

- В ходе курсовой работы были пройдены все этапы разработки качественного программного обеспечения. Наша команда создала телеграм-бот, который собирает статистику по COVID-19 и отправляет пользователю.



