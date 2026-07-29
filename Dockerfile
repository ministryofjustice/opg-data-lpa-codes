FROM golang:1.26.5@sha256:3aff6657219a4d9c14e27fb1d8976c49c29fddb70ba835014f477e1c70636647 AS build-env

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
FROM public.ecr.aws/lambda/provided:al2023@sha256:26136a72871f0d0f9948a98a4568010b3aa210cd7bcb7dd6b51b606fe743b79a AS base

RUN dnf upgrade -y --releasever=latest && \
    dnf clean all

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
