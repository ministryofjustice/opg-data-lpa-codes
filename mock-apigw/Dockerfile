FROM golang:1.25.5@sha256:6cc2338c038bc20f96ab32848da2b5c0641bb9bb5363f2c33e9b7c8838f9a208 AS build-env

WORKDIR /app

COPY go.mod .
COPY go.sum .

RUN go mod download

COPY mock-apigw mock-apigw
COPY internal internal

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o /go/bin/main ./mock-apigw

FROM alpine:3@sha256:25109184c71bdad752c8312a8623239686a9a2071e8825f20acb8f2198c3f659

COPY --from=build-env /go/bin/main /var/task/main

RUN addgroup -S app && adduser -S -g app app
USER app

ENTRYPOINT [ "/var/task/main" ]
