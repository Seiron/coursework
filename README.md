# Моделирование введения запрета смешанного режима работы маркетплейсов
[Текст исследовательской работы в формате pdf](https://github.com/Seiron/coursework/blob/main/vkr.pdf)
### Теоретическая часть работы
В теоретической части работы разрабатывается теоретико-игровая модель взаимодействия игроков на маркетплейсе. Код со всеми вычислениями и построением графиков из работы можно найти [здесь](https://github.com/Seiron/coursework/blob/main/model_analysis.ipynb)

### Эмпирическая часть работы

В эмпирической части работы проверяются существенные для теоретико-игровой модели предпосылки. Решается задача выявления предвзятости алгоритма рекомендаций в пользу определенных товаров на основе открытых данных, которая может рассматриваться отдельно от остальной работы

[Наивный подход](https://github.com/Seiron/coursework/blob/main/naiive_analysis.ipynb) - менее точный, но более доступный (с точки зрения необходимой информации) метод оценки на основе прокси-переменной

[ML-подход](https://github.com/Seiron/coursework/blob/main/ml_analysis.ipynb) - альтернативный способ оценки на основе методов машинного обучения

### Данные
Данные о характеристиках товаров получены путем парсинга сайта [Ozon](https://www.ozon.ru/)

Код для парсера с комментариями можно найти [здесь](https://github.com/Seiron/coursework/blob/main/data_parser.py). Коды элементов, вероятно, поменялись, но общая структура та же. Использовались неспецифические популярные на маркетплейсе запросы, для работы парсера нужен соответствующий файл с запросами [search_queries.csv](https://github.com/Seiron/coursework/blob/main/search_queries.csv)

[algo_data.csv](https://github.com/Seiron/coursework/blob/main/algo_data.csv) - результат работы парсера + данные о товарах с сервиса Ozon.Data, объединенные в один файл

Отдельно данные с сервиса Ozon.Data можно посмотреть [здесь](https://data.ozon.ru/) и [здесь](https://docs.google.com/spreadsheets/d/1cvfUF_dbU1U6hzlV9NBni2RvJyYOZg_P/edit?usp=drive_link&ouid=108249924862817693205&rtpof=true&sd=true) (во втором случае представлены только релевантные для исследования категории, данные за 01.04.2024)
