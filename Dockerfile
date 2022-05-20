FROM maven:3-eclipse-temurin-17 AS builder
COPY . /src
RUN cd /src && mvn clean && mvn package

FROM eclipse-temurin:17-focal
RUN apt-get update && apt-get install -y firefox firefox-geckodriver && rm -rf /var/lib/apt/lists/*
RUN mkdir -p /dist/libs
COPY --from=builder /src/target/lufa-weekly-canceler-*.jar /dist
COPY --from=builder /src/target/libs/* /dist/libs/
WORKDIR /dist
CMD java -jar lufa-weekly-canceler-*.jar