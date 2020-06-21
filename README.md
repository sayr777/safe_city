Введение
========

Сервис обеспечивает взаимодействие АПК БГ с системой мониторинга
транспортных средств (РНИС).

Требования к интеграции указаны в документе заказчика *Документ Заказчика-
требования к интеграции.docx*

Описание функций
============================================

Реализованые методы:

1.  Получение списка ТС, зарегистрированных в РНИС

2.  Получение навигационного сообщения по OID АТТ

3.  Получение навигационных сообщений от ТС по uuid транспортного предприятия -
    владельца

В качестве токена используется uuid предприятия

Получение справочника ТС
------------------------

Авторизация по токену

Метод возвращает список всех ТС зарегистрированных в РНИС НО, требуемой
структуры:

| Название  | Описание                                                                                                                     | Тип    |
|-----------|------------------------------------------------------------------------------------------------------------------------------|--------|
| id        | Уникальный идентификатор транспортного средства в РНИС НО                                                                    | string |
| idDev     | OID АТТ                                                                                                                      | uint   |
| name      | название объекта/ТС (может быть любым как удобно пользователю видеть этот объект в списке объектов в программе для удобства) | string |
| groupname | Наименование подсистемы РНИС НО к которой привязано ТС                                                                       | string |
| createts  | год выпуска ТС                                                                                                               | string |
| markats   | марка и модель ТС                                                                                                            | string |
| typets    | тип ТС                                                                                                                       | string |
| gosnumber | государственный номер ТС                                                                                                     | string |
| vin       | VIN номер ТС                                                                                                                 | string |
| org_id    | Уникальный идентификатор организации -владельца ТС в РНИС НО                                                                 | string |
| org_name  | Полное наименование организации -владельца ТС                                                                                | string |
| org_inn   | ИНН организации -владельца ТС. Передается если заполнено в РНИС НО                                                           | string |

[GET] http://IP:PORT/v.1/vehicles_dic/<token>



Получение навигационного сообщения по OID АТТ
---------------------------------------------

Авторизация по токену

Метод получает на вход idDev (идентификатор АТТ)

Метод возвращает структуру навигационного сообщения по идентификатору
абонентского телематического терминала:

| Название  | Описание                                                           | Тип    |
|-----------|--------------------------------------------------------------------|--------|
| id        | Уникальный идентификатор транспортного средства в РНИС НО          | string |
| idDev     | OID АТТ                                                            | uint   |
| lat       | Широта местоположения ТС                                           | float  |
| lon       | Долгота местоположения ТС                                          | float  |
| angle     | Курсовой угол движения ТС                                          | uint   |
| speed     | Скорость ТС                                                        | uint   |
| time      | Время навигационного события                                       | uint   |
| date      | Дата навигационного события                                        | text   |
| typets    | Тип ТС                                                             | string |
| gosnumber | ГРЗ ТС                                                             | string |
| vin       | VIN номер ТС                                                       | string |
| org_id    | Уникальный идентификатор организации -владельца ТС в РНИС НО       | string |
| org_name  | Полное наименование организации -владельца ТС                      | string |
| org_inn   | ИНН организации -владельца ТС. Передается если заполнено в РНИС НО | string |


[GET] http://IP:PORT/v.1/idDev:<path:idDev>/<path:token>



Получение крайних навигационных сообщений по транспортным средствам организации
-------------------------------------------------------------------------------

Авторизация по токену

Метод получает на вход org_id

Метод возвращает список структур навигационных сообщений для всех ТС данной
организации:

| Название  | Описание                                                           | Тип    |
|-----------|--------------------------------------------------------------------|--------|
| id        | Уникальный идентификатор транспортного средства в РНИС НО          | string |
| idDev     | OID АТТ                                                            | uint   |
| lat       | Широта местоположения ТС                                           | float  |
| lon       | Долгота местоположения ТС                                          | float  |
| angle     | Курсовой угол движения ТС                                          | uint   |
| speed     | Скорость ТС                                                        | uint   |
| time      | Время навигационного события                                       | uint   |
| date      | Дата навигационного события                                        | text   |
| typets    | Тип ТС                                                             | string |
| gosnumber | ГРЗ ТС                                                             | string |
| vin       | VIN номер ТС                                                       | string |
| org_id    | Уникальный идентификатор организации -владельца ТС в РНИС НО       | string |
| org_name  | Полное наименование организации -владельца ТС                      | string |
| org_inn   | ИНН организации -владельца ТС. Передается если заполнено в РНИС НО | string |

[GET] http://IP:PORT/v.1/messages/org_id:<path:org_id>/<path:token>



Архитектура сервиса (Алгоритм работы сервиса)
=============================================

1. Периодически, сервис должен запрашивать из РНИС следующие сущности:

-   Перечень организаций;

-   Справочник типов ТС;

-   Справочник моделей ТС;

-   Справочник марок ТС;

-   Реестр БНСО;

-   Реестр ТС;

-   Реестр соответствия БНСО и ТС

Период опроса должен задаваться в переменные окружения GET_DATA_TIMEOUT в
минутах.

Вид запроса для получения реестра организаций:

SELECT uuid, name_full, inn FROM public.units;

Возвращаемая структура должна содержать:

-   uuid - уникальный идентификатор предприятия в РНИС

-   name_full - наименование организации

-   inn - ИНН Организации

Вид запроса для получения типа ТС:

SELECT uuid, name FROM public.vehicle_types WHERE deleted_at is NULL

Возвращаемая структура должна содержать:

-   uuid - идентификатор типа ТС

-   name - наименование типа ТС

Вид запроса для получения справочника модели ТС:

SELECT uuid, name FROM public.vehicle_models WHERE deleted_at is NULL

Возвращаемая структура должна содержать:

-   uuid - идентификатор модели ТС

-   name - наименование модели ТС

Вид запроса для получения справочника марки ТС:

SELECT uuid, name FROM public.vehicle_marks WHERE deleted_at is NULL

Возвращаемая структура должна содержать:

-   uuid - идентификатор марки ТС

-   name - наименование марки ТС

Вид запроса для получения реестра БНСО:

SELECT uuid, bnso_number FROM public.bnso WHERE deleted_at is NULL

Возвращаемая структура должна содержать:

-   uuid - идентификатор БНСО

-   name - OID БНСО

Вид запроса для получения реестра соответствия БНСО-ТС:

SELECT bnso_uuid, vehicle_uuid FROM public.bnso2vehicles WHERE deleted_at is
NULL

Возвращаемая структура должна содержать:

-   bnso_uuid - идентификатор БНСО

-   vehicle_uuid - идентификатор ТС

Вид запроса для получения реестра ТС:

SELECT uuid, state_number, vehicle_type_uuid, release_year, vin,
vehicle_mark_uuid, current_bnso_uuid, unit_uuid, component, vehicle_model_uuid,

idle_time, status_change_time,

paid, vehicle_capacity_integer

FROM public.vehicles WHERE deleted_at is NULL AND current_bnso_uuid is not NULL

Возвращаемая структура должна содержать:

-   uuid - идентификатор ТС

-   state_number - ГРЗ ТС

-   vehicle_type_uuid - тип ТС

-   release_year - год выпуска ТС

-   vin - VIN ТС

-   vehicle_mark_uuid - марка ТС

-   current_bnso_uuid - uuid БНСО

-   unit_uuid - uuid организации

-   component - подсистема РНИС

-   vehicle_model_uuid - uuid модели ТС

2. Сервис по запросу клиента (uuid организации) должен сформировать запрос по
OID БНСО к gRPC интерфейсу РНИС и далее сформировать структуру, требуемую в
документе *Документ Заказчика- требования к интеграции.docx*

Схема информационного взаимодействия сервиса представлена на рисунке №1.

![](media/f788d86507c555d33692a1783feea555.png)

Рисунок Схема взаимодействия сервиса

Требования к конфигурированию сервиса
=====================================

Конфигурирование сервиса производится через переменные окружения

-   'TOKEN' = '213d3f34gvb%fgd45HJH' \# ключ доступа. Тип STRING (255)

-   'gRPC_URL' = 'rnis-tm.t1-group.ru:18082' \# интерфейс gRPC сервиса. Тип
    STRING

-   'PG_SQL' = 'postgresql://postgres\@10.10.21.25:5432' \# БД РНИС НО. Тип
    STRING

-   'GET_DATA_TIMEOUT' = 10 \# Время опроса сущностей БД в минутах. Тип INTEGER

-   'SQLLITE_IN_MEMORY' = True \# Внутренняя БД в памяти? Тип BOOL
    
-   'FLASK_ENV' = 'development' запуск сервисав режиме development

Требования к логированию (сообщения об ошибках)
===============================================

Все логи передаются в stdout

Логируются следующие действия:

-   Старт и остановка сервиса

-   Подключение к gRPC

-   Подключение к PostgreSQL.

-   Получение списков сущностей РНИС

-   Запросы к сервису

Требования к мониторингу
========================

Сервис генерирует следующие матрики Prometheus:

-   сервис работоспособен;

-   доступ к PGSQL есть;

-   доступ к gRPC есть;

-   кол-во запросов в минуту

-   количество ответов в минуту

Метрики доступны по пути
http://ip:port/metrics

Развертывание сервиса
==========================

Сервис работает из Docker контейнера
Dockerfile:
`FROM python:3.7
ENV GRPC_PYTHON_VERSION 1.27.2
RUN python -m pip install --upgrade pip
RUN pip install grpcio==${GRPC_PYTHON_VERSION} grpcio-tools==${GRPC_PYTHON_VERSION}
RUN mkdir /code
COPY . /code
WORKDIR /code
ENV gRPC_URL = '10.10.21.22:5587'
ENV pSQL_URL = 'postgresql://postgres@10.10.21.25:5432/'
RUN pip install -r requirements.txt
RUN chmod +x ./run.sh
EXPOSE 8000
ENTRYPOINT ./run.sh`

Используется сценарий CI 

`image: tempik/dind-ci-image:latest
variables:
  REGISTRY_URL: hub.t1-group.ru
  CONTAINER_NAME: rnis/safe_city
  IMAGE_NAME_BASE: $REGISTRY_URL/$CONTAINER_NAME
stages:
  - build
build:
  stage: build
  only:
    - master
  script:
    - BUILDTAG=$(TZ=":Europe/Moscow" date +%Y%m%d.%H%M)
    - docker build
        --cache-from $IMAGE_NAME_BASE:latest
        --tag $IMAGE_NAME_BASE:$BUILDTAG
        --tag $IMAGE_NAME_BASE:latest .
    - echo "${REGISTRY_PASSWORD}" | docker login
        --username "${REGISTRY_USER}"
        --password-stdin
        $REGISTRY_URL
    - docker push $IMAGE_NAME_BASE:$BUILDTAG
    - docker push $IMAGE_NAME_BASE:latest
    - docker logout $REGISTRY_URL
    - docker rmi $IMAGE_NAME_BASE:$BUILDTAG
    - curl
        --get
        --data-urlencode "message=Новая сборка ${IMAGE_NAME_BASE}:${BUILDTAG}"
        "http://crierbot.appspot.com/${CRIER_TOKEN}/send?"`





##Порты
'8891' - порт prometheus exporter (устанавливается в env)

'8000' - порт приложения (устанавливается в env)

'9002' - порт suppervisor (устанавливается в supervisor.conf)

##Метрики prometheus
flask_exporter_info - сервис работает

flask_http_request_total -   количество запросов


