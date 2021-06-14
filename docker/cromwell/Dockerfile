FROM openjdk:8-stretch

COPY --from=library/docker:latest /usr/local/bin/docker /usr/local/bin/docker

ARG CROMWELL_VERSION="53.1"
WORKDIR /

RUN wget "https://github.com/broadinstitute/cromwell/releases/download/${CROMWELL_VERSION}/cromwell-${CROMWELL_VERSION}.jar" -O /cromwell.jar

EXPOSE 7338
COPY docker/cromwell/cromwell.conf /