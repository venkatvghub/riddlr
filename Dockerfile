FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python3 python3-pip python3-dev libpq-dev 

# We copy just the requirements.txt first to leverage Docker cache
COPY ./requirements2.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install Psycopg2 && pip3 install -r requirements.txt

COPY . /app

CMD ["/app/start.sh"]

EXPOSE 8082

#ENTRYPOINT [ "python" ]

#CMD [ "app.py" ]

