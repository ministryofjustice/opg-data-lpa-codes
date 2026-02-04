FROM golang:1.25.6@sha256:0032c99f1682c40dca54932e2fe0156dc575ed12c6a4fdec94df9db7a0c17ab0 AS build-env

ARG TARGETOS
ARG TARGETARCH

WORKDIR /app

COPY --link go.mod go.sum ./
RUN go mod download
RUN go install github.com/go-delve/delve/cmd/dlv@latest

COPY --link main.go main.go
COPY --link internal internal

RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH go build -gcflags "all=-N -l" -a -installsuffix cgo -o /go/bin/main-dbg .
RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH go build -a -installsuffix cgo -o /go/bin/main .

# Base image
FROM public.ecr.aws/lambda/provided:al2023.2026.01.19.11@sha256:7ad7e21e89618eeaa3842bc089ab924cefa9f8f7df13deae44055ec7f161c0b2 AS base

COPY --from=build-env /go/bin/main ./main

ENTRYPOINT [ "./main" ]

# Local development with debugging
FROM base AS debug

COPY --from=build-env /go/bin/dlv ./dlv
COPY --from=build-env /go/bin/main-dbg ./main

ENTRYPOINT [ "/usr/local/bin/aws-lambda-rie", "./dlv", "exec", "--headless", "--continue", "--listen", ":4040", "--api-version=2", "--accept-multiclient", "./main" ]

# Default production image
FROM base AS production

# not necessary in a production image
RUN rm /usr/local/bin/aws-lambda-rie
