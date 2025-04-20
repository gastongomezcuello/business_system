FROM python:3.13


RUN useradd -m container-admin
USER container-admin


WORKDIR /app


COPY . /app/


RUN pip install --no-cache-dir -r requirements.txt


EXPOSE 8000


CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]