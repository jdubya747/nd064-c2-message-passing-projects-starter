FROM python:3.9-alpine
#FROM python:2.7
WORKDIR .

RUN apk add --no-cache gcc musl-dev linux-headers geos libc-dev postgresql-dev build-base python3-dev
COPY requirements.txt requirements.txt

RUN python3 -m pip install -U pip
RUN pip3 install --upgrade setuptools
RUN pip3 install -r requirements.txt

EXPOSE 5000
EXPOSE 5005

COPY . .
CMD ["flask", "run", "--host", "0.0.0.0"]