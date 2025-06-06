FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

ENV PORT 8080
EXPOSE 8080

CMD ["flask", "run", "--host=0.0.0.0", "--port=8080"]
