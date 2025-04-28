FROM python:3.12.6-bookworm

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
EXPOSE 8000

RUN pip install --upgrade pip wheel
RUN pip install "poetry==1.8.3"

RUN poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock ./

RUN poetry install

COPY . .

RUN chmod +x app/run_main.py
RUN chmod +x app/prestart.sh

ENTRYPOINT ["app/prestart.sh"]
CMD ["python", "-m", "app.run_main"]
