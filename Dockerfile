FROM golang:1.26.2@sha256:b54cbf583d390341599d7bcbc062425c081105cc5ef6d170ced98ef9d047c716 AS build

WORKDIR /app

COPY --link go.mod go.sum ./
RUN go mod download

COPY --link main.go main.go
COPY --link internal internal

RUN GOOS=${TARGETOS} GOARCH=${TARGETARCH} CGO_ENABLED=0 go build -a -installsuffix cgo -o main .

FROM public.ecr.aws/lambda/provided:al2023@sha256:26136a72871f0d0f9948a98a4568010b3aa210cd7bcb7dd6b51b606fe743b79a AS local

WORKDIR /app

COPY --from=build /app/main ./main

ENTRYPOINT [ "/usr/local/bin/aws-lambda-rie", "./main" ]

FROM scratch AS production

WORKDIR /app

COPY --from=build /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --from=build /app/main ./main

ENTRYPOINT ["./main"]
