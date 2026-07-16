FROM golang:1.26.2@sha256:b54cbf583d390341599d7bcbc062425c081105cc5ef6d170ced98ef9d047c716 AS build-env

WORKDIR /app

COPY go.mod .
COPY go.sum .

RUN go mod download

COPY mock-apigw mock-apigw
COPY internal internal

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o /go/bin/main ./mock-apigw

FROM alpine:3@sha256:28bd5fe8b56d1bd048e5babf5b10710ebe0bae67db86916198a6eec434943f8b

COPY --from=build-env /go/bin/main /var/task/main

RUN addgroup -S app && adduser -S -g app app
USER app

ENTRYPOINT [ "/var/task/main" ]
