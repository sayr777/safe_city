FROM python:3.7
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
ENTRYPOINT ./run.sh





