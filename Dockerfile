FROM python:3.11-slim

WORKDIR /app

COPY poetry.lock .

RUN poetry export -f requirements.txt > requirements.txt
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]