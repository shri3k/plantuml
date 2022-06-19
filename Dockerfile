FROM python:latest AS builder
ARG VERSION
WORKDIR /app
COPY ./download_url.py .
RUN curl -L "$(python download_url.py --version=${VERSION:-latest})" -o plantuml.jar

FROM openjdk:12-jdk-oraclelinux7
RUN  yum install graphviz -y

WORKDIR /app
COPY --from=builder /app/plantuml.jar ./
WORKDIR /tmp
ENTRYPOINT ["java", "-jar", "/app/plantuml.jar"]
