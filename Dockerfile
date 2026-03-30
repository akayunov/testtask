FROM python:3.14-alpine

WORKDIR /payment_app
RUN pip install poetry==2.3.2
RUN poetry config virtualenvs.create false
RUN python3 -m venv /app
ENV VIRTUAL_ENV=/app
COPY src/ps /payment_app/src/ps/
COPY pyproject.toml poetry.toml README.md /payment_app/
RUN poetry install  --no-root --only main
RUN poetry build -f wheel && /app/bin/pip install --no-deps -U dist/*.whl


FROM python:3.14-alpine

RUN apk add busybox-extras
ENV PATH="/app/bin:${PATH}"
COPY --from=0 /app /app
CMD ["payment"]