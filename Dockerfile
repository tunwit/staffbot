FROM python:3.11.10-alpine3.20
WORKDIR /code 
COPY requirements.txt . 
RUN pip install -r requirements.txt
RUN apk add --no-cache ffmpeg
COPY src/ .
CMD ["python","-u","./main.py"]

