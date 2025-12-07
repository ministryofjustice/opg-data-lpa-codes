FROM golang:1.25.5@sha256:20b91eda7a9627c127c0225b0d4e8ec927b476fa4130c6760928b849d769c149 AS build-env

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
FROM public.ecr.aws/lambda/provided:al2023.2025.11.11.00@sha256:eaa5988b7e760cdc511de0647a36110af1b453aade2f565eeb8157e16bc97a86 AS base

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