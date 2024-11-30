FROM python:latest


WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY server.py ./
EXPOSE 8950
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8950"]