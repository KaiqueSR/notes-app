FROM python:3.11-alpine
WORKDIR /app
ENV FLASK_APP=app
ENV FLASK_DEBUG=true
ENV FLASK_RUN_HOST=0.0.0.0
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["flask", "run"]