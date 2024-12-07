FROM python:latest

ENV PYTHONUNBUFFERED=1

WORKDIR /usr/src/app
RUN mkdir data 
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY server.py ./

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8950"]