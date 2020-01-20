FROM python:3

COPY /code/requirements.txt /app/requirements.txt
WORKDIR /app

RUN pip install -r requirements.txt

COPY /code .

ENTRYPOINT ["python"]
CMD ["genetic.py"]
