FROM python:3.12-slim-bookworm
ARG BUILD_VERSION=0.1.0
LABEL io.hass.version="${BUILD_VERSION}" io.hass.type="app" io.hass.arch="amd64|aarch64"
LABEL org.opencontainers.image.source="https://github.com/ValentineAlan/omnivoice-connect"
LABEL org.opencontainers.image.licenses="Apache-2.0"
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN groupadd -g 568 apps && useradd -u 568 -g 568 -M apps && mkdir /app /data && chown 568:568 /data
WORKDIR /app
COPY server.py protocol.py ./
COPY static/ ./static/
EXPOSE 8099
CMD ["python", "server.py"]
