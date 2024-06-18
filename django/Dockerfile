FROM python:3.10-bookworm

RUN mkdir -p /django
WORKDIR /django

COPY ./Pipfile /django/
COPY ./Pipfile.lock /django/
RUN pip install --upgrade pip && \
    pip install pipenv && \
    pipenv install --deploy --system

COPY . /django/

EXPOSE 8000

CMD ["sh", "-c", "python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8000"]