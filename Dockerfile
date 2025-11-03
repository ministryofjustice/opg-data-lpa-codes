FROM golang:1.24.6@sha256:8d9e57c5a6f2bede16fe674c16149eee20db6907129e02c4ad91ce5a697a4012 AS build-env

WORKDIR /app

COPY --link go.mod go.sum .
RUN go mod download

COPY --link main.go main.go
COPY --link internal internal

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o /go/bin/main .

FROM public.ecr.aws/lambda/provided:al2023.2025.10.22.12@sha256:b06651e2b9351d9c2a9ed23c4a324275a6ac9e38868e9a35cefd4a879d08bc26

COPY --from=build-env /go/bin/main ./main

ENTRYPOINT [ "./main" ]
