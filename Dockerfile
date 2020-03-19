FROM python:3.7.2-alpine3.9
RUN apk add --no-cache python3-dev libstdc++ && \
    apk add --no-cache g++ && \
    ln -s /usr/include/locale.h /usr/include/xlocale.h
RUN set -ex && \
        apk add --update --no-cache \
        alpine-sdk \
        make \
        python-dev \
        tzdata \
        ca-certificates \
        gcc \
        g++ \
        curl \
        python3 \
        python3-dev \
        && \
	    cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime && \
	    echo "Europe/Moscow" > /etc/timezone \
        apk add --no-cache \
            python3 \
            tzdata && \
	cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime && \
	echo "Europe/Moscow" > /etc/timezone
COPY . /code
WORKDIR /code
RUN apk update && apk add postgresql-dev gcc musl-dev
RUN pip3 install --upgrade pip
RUN pip3 install psycopg2-binary
RUN python3 -m pip install grpcio --ignore-installed
RUN python3 -m pip install grpcio-tools
RUN pip3 install -r requirements.txt
RUN chmod +x ./run.sh

EXPOSE 8000
ENTRYPOINT ./run.sh

