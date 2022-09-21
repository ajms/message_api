ARG BASEIMAGE

FROM ${BASEIMAGE}

WORKDIR /app
COPY . .
# "--root-path", "/message-api",
CMD ["uvicorn", "src.main:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "8000"]
