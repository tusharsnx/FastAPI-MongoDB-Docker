FROM ubuntu

RUN apt-get update -y
RUN apt-get install -y python && apt-get install -y pip

COPY /app /home/app

RUN pip install -r ./home/app/requirements.txt

WORKDIR /home/app

ENTRYPOINT ["uvicorn", "main:app", "--host", "0.0.0.0", "--workers", "100"  ]