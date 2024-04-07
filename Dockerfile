FROM python

WORKDIR /app

RUN pip install --upgrade mailru-im-bot
RUN pip install psycopg2
RUN pip install schedule


COPY . .

#EXPOSE 8888

CMD [ "python", "main.py" ]