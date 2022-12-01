FROM ubuntu

RUN apt update
RUN apt install python3-pip -y
RUN pip3 install Flask
RUN pip3 install Flask-SQLAlchemy
RUN pip3 install flask-wtf
RUN pip3 install email_validator
RUN pip3 install flask_bcrypt
RUN pip3 install flask_login
RUN pip3 install requests
RUN pip3 install bs4

WORKDIR /app

COPY . .

CMD ["python3", "run.py"]