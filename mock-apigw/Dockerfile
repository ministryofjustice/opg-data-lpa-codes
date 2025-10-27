FROM golang:1.24.6 AS build-env

WORKDIR /app

COPY go.mod .
COPY go.sum .

RUN go mod download

COPY mock-apigw mock-apigw

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o /go/bin/main ./mock-apigw

FROM alpine:3

COPY --from=build-env /go/bin/main /var/task/main

RUN addgroup -S app && adduser -S -g app app
USER app

ENTRYPOINT [ "/var/task/main" ]
