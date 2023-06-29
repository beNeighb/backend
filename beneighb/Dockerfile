# pull official base image
FROM python:3.12.0b3-alpine3.18

# set work directory
WORKDIR /usr/src/beneighb

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1  # Prevents Python from writing pyc files to disc
ENV PYTHONUNBUFFERED 1  # Prevents Python from buffering stdout and stderr

# install psycopg2 dependencies
RUN apk update \
    && apk add postgresql-dev gcc python3-dev musl-dev

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/beneighb/entrypoint.sh
RUN chmod +x /usr/src/beneighb/entrypoint.sh

# copy project
COPY . .

# run entrypoint.sh
ENTRYPOINT ["/usr/src/beneighb/entrypoint.sh"]
