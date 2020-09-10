FROM python:3.7
ENV GRPC_PYTHON_VERSION 1.27.2
RUN python -m pip install --upgrade pip
RUN pip install grpcio==${GRPC_PYTHON_VERSION} grpcio-tools==${GRPC_PYTHON_VERSION}
EXPOSE 8000 8891 9001
RUN mkdir /code
COPY . /code
WORKDIR /code

ENV pSQL_URL='postgresql://postgres@10.10.21.25:5432/'
ENV API_TOKEN='8d6fbe03e99f4b13966e622981c9a11f'
ENV gRPC_URL='10.10.21.22:5587'
ENV PROMETHEUS_PORT='8891'
ENV FUNC_PORT='8000'
ENV PGSQL_PERIOD='20'

RUN pip install -r requirements.txt
RUN pip install python-dotenv
COPY supervisord.conf /etc/supervisor/conf.d/
RUN cp /usr/share/zoneinfo/Europe/Moscow /etc/localtime && echo "Europe/Moscow" > /etc/timezone
CMD ["supervisord"]













