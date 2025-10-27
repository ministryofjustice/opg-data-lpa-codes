FROM golang:1.25.2@sha256:1c91b4f4391774a73d6489576878ad3ff3161ebc8c78466ec26e83474855bfcf AS build-env

WORKDIR /app

COPY --link go.mod go.sum .
RUN go mod download

COPY --link main.go main.go
COPY --link internal internal

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o /go/bin/main .

FROM public.ecr.aws/lambda/provided:al2023.2025.10.22.12

COPY --from=build-env /go/bin/main ./main

ENTRYPOINT [ "./main" ]
