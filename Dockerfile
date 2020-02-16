FROM ubuntu

RUN apt-get update
RUN apt-get install -y python3
RUN apt-get install -y python3-pip
RUN apt-get install -y gfortran

RUN mkdir /pipeline
COPY . /pipeline
WORKDIR /pipeline

RUN ./install.sh

CMD ["python3", "pipeline.py"]