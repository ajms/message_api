ARG BASEIMAGE

FROM ${BASEIMAGE}

WORKDIR /app
COPY . .

# "--root-path", "/message-api","--proxy-headers",
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
