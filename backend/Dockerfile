FROM python:3.13
WORKDIR /app

COPY . .

RUN pip install -r requirements.txt
RUN pip install watchfiles
RUN pip install selenium
RUN pip install selenium webdriver-manager
RUN pip install pytest
EXPOSE 8000
CMD ["python", "-m", "watchfiles", "--filter", "python", "python manage.py runserver 0.0.0.0:8000"]