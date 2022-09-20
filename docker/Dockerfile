ARG BASEIMAGE

FROM ${BASEIMAGE}

WORKDIR /app
COPY . .

CMD ["uvicorn", "src.main:app", "--root-path", "/message-api", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
