#!/bin/bash

# Nginx entrypoint script for Django KPI Tracker
# Generates nginx configuration from templates using environment variables

# Set defaults if not provided
export NGINX_PORT=${NGINX_PORT:-80}
export NGINX_SSL_PORT=${NGINX_SSL_PORT:-443}
export NGINX_SERVER_NAME=${NGINX_SERVER_NAME:-_}
export NGINX_WORKER_PROCESSES=${NGINX_WORKER_PROCESSES:-auto}
export NGINX_KEEPALIVE_TIMEOUT=${NGINX_KEEPALIVE_TIMEOUT:-65}
export NGINX_CLIENT_MAX_BODY_SIZE=${NGINX_CLIENT_MAX_BODY_SIZE:-100M}
export NGINX_PROXY_READ_TIMEOUT=${NGINX_PROXY_READ_TIMEOUT:-60s}
export NGINX_PROXY_SEND_TIMEOUT=${NGINX_PROXY_SEND_TIMEOUT:-60s}
export NGINX_HTTPS_ENABLED=${NGINX_HTTPS_ENABLED:-false}
export NGINX_SSL_PROTOCOLS=${NGINX_SSL_PROTOCOLS:-"TLSv1.2 TLSv1.3"}

# SSL configuration
# Convert to lowercase for comparison
HTTPS_ENABLED_LOWER=$(echo "$NGINX_HTTPS_ENABLED" | tr '[:upper:]' '[:lower:]')

if [ "$HTTPS_ENABLED_LOWER" = "true" ]; then
    export SSL_CERTIFICATE_PATH="/etc/ssl/${NGINX_SSL_CERT_FILENAME:-cert.crt}"
    export SSL_CERTIFICATE_KEY_PATH="/etc/ssl/${NGINX_SSL_CERT_KEY_FILENAME:-cert.key}"
    export NGINX_SSL_CONFIG="include /etc/nginx/ssl-common.conf;"
    
    # Generate SSL config
    env_vars_ssl=$(printenv | cut -d= -f1 | sed 's/^/$/g' | paste -sd, -)
    envsubst "$env_vars_ssl" < /etc/nginx/ssl-common.conf.template > /etc/nginx/ssl-common.conf
else
    # Create empty file if HTTPS is disabled
    export NGINX_SSL_CONFIG=""
    echo "# HTTPS disabled" > /etc/nginx/ssl-common.conf
fi

# Generate nginx configs from templates
env_vars=$(printenv | cut -d= -f1 | sed 's/^/$/g' | paste -sd, -)

envsubst "$env_vars" < /etc/nginx/nginx.conf.template > /etc/nginx/nginx.conf
envsubst "$env_vars" < /etc/nginx/proxy.conf.template > /etc/nginx/proxy.conf
envsubst "$env_vars" < /etc/nginx/conf.d/default.conf.template > /etc/nginx/conf.d/default.conf

echo "Nginx configuration generated successfully"
echo "HTTPS Enabled: ${NGINX_HTTPS_ENABLED}"
echo "Server Name: ${NGINX_SERVER_NAME}"

# Start nginx
exec nginx -g 'daemon off;'
