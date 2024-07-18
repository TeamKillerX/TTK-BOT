FROM rendyprojects/python:latest

WORKDIR /usr/src/app
COPY . .
RUN pip3 install --upgrade pip setuptools
RUN pip3 install -r requirements.txt

CMD ["python3", "main.py"]
