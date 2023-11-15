FROM --platform=Linux/amd64 amazon/aws-cli:2.13.34

ENV PATH="${PATH}:/usr/local/bin/"

COPY ./app/ /app/

ENTRYPOINT ["/bin/bash", "-c"]