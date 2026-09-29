FROM golang:1.27.0@sha256:4013ae0f9e7994f8535c58c811f8f863fbed38b72e0d51e6592156f758d66146 AS build-env

WORKDIR /app

COPY go.mod .
COPY go.sum .

RUN go mod download

COPY mock-apigw mock-apigw
COPY internal internal

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o /go/bin/main ./mock-apigw

FROM alpine:3@sha256:294b683cb724975bec92580e1e685676bd4b50bda910ddb8c51d4cabeaec77e6

COPY --from=build-env /go/bin/main /var/task/main

RUN addgroup -S app && adduser -S -g app app
USER app

ENTRYPOINT [ "/var/task/main" ]
