FROM golang:1.25.3@sha256:6d4e5e74f47db00f7f24da5f53c1b4198ae46862a47395e30477365458347bf2 AS build-env

WORKDIR /app

COPY --link go.mod go.sum .
RUN go mod download

COPY --link main.go main.go
COPY --link internal internal

RUN CGO_ENABLED=0 GOOS=linux GOARCH=amd64 go build -a -installsuffix cgo -o /go/bin/main .

FROM public.ecr.aws/lambda/provided:al2023.2025.11.11.00@sha256:eaa5988b7e760cdc511de0647a36110af1b453aade2f565eeb8157e16bc97a86

COPY --from=build-env /go/bin/main ./main

ENTRYPOINT [ "./main" ]
