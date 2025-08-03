# ===== Stage 1: Build =====
FROM golang:1.24 AS builder

# Set environment for Go modules
ENV CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64

WORKDIR /app

# Install dependencies first (better caching)
COPY go.mod go.sum ./
RUN go mod download

# Copy source code
COPY . .

# Build the Go binary
RUN go build -o gateway main.go


# ===== Stage 2: Run =====
FROM alpine:3.22

WORKDIR /app

# Install CA certificates for HTTP requests
RUN apk --no-cache add ca-certificates

# Copy binary from builder
COPY --from=builder /app/gateway .

# Expose gateway port
EXPOSE 8080

# Default ENV so app knows it’s inside Docker
ENV RUNNING_IN_DOCKER=true \
    GIN_MODE=release

# Run the gateway
CMD ["./gateway"]
