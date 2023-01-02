FROM ubuntu

RUN apt update
RUN apt install python3-pip -y
RUN pip3 install Flask
RUN pip3 install Flask-SQLAlchemy==2.5.1
RUN pip3 install flask-wtf
RUN pip3 install email_validator
RUN pip3 install flask_bcrypt
RUN pip3 install flask_login
RUN pip3 install requests
RUN pip3 install bs4
RUN pip3 install waitress
RUN pip3 install psycopg2-binary
RUN pip3 install python-consul
RUN pip3 install apiflask

WORKDIR /app

COPY . .

CMD ["waitress-serve", "--listen=*:80", "primerjalnik:app"]