FROM golang:1.25.3@sha256:6bac879c5b77e0fc9c556a5ed8920e89dab1709bd510a854903509c828f67f96 AS build-env

WORKDIR /app

COPY --link go.mod go.sum .
RUN go mod download

COPY --link main.go main.go
COPY --link internal internal

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o /go/bin/main .

FROM public.ecr.aws/lambda/provided:al2023.2025.10.22.12

COPY --from=build-env /go/bin/main ./main

ENTRYPOINT [ "./main" ]
