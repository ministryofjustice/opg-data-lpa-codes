FROM golang:1.24.6 AS build-env

WORKDIR /app

COPY --link go.mod go.sum .
RUN go mod download

COPY --link main.go main.go
COPY --link internal internal

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o /go/bin/main .

FROM public.ecr.aws/lambda/provided:al2023.2025.10.05.11

COPY --from=build-env /go/bin/main ./main

ENTRYPOINT [ "./main" ]
