FROM python:3.14

RUN pip install poetry
WORKDIR /payment_app_test/tests
COPY pyproject.toml poetry.toml /payment_app_test/
COPY tests /payment_app_test/tests/

RUN poetry config virtualenvs.create false
RUN python3 -m venv /payment_app_test/.venv
ENV VIRTUAL_ENV=/payment_app_test/.venv
RUN poetry install --no-root --only dev

ENV PATH="/payment_app_test/.venv/bin:${PATH}"
