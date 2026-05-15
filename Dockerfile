FROM golang:1.26.0@sha256:c83e68f3ebb6943a2904fa66348867d108119890a2c6a2e6f07b38d0eb6c25c5 AS build-env

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
FROM public.ecr.aws/lambda/provided:al2023@sha256:2578d956647acc9085f2da8c58f0d1ad76f7f2dbc7dc610e68ba5b1099c66a55 AS base

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
