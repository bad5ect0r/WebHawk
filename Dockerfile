FROM python:3.8.5
ENV DJANGO_SUPERUSER_PASSWORD=change_me
ENV PYTHONUNBUFFERED=1
ENV STATIC_ROOT=/static
ENV DEBUG=False
RUN mkdir /code
RUN mkdir /static
COPY . /code
WORKDIR /code
RUN pip install -r requirements.txt
RUN python manage.py migrate --no-input
RUN python manage.py createsuperuser --no-input --username admin --email admin@example.com
RUN pip install gunicorn
RUN python manage.py collectstatic --no-input
EXPOSE 8000
CMD ./runprod.sh
