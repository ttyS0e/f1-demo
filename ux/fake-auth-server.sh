#!/usr/bin/env bash
# Pretend login server for local testing.
#
# Listens on 127.0.0.1:8000 and:
#   - answers CORS preflight (OPTIONS) requests for any path
#   - answers POST /auth: 200 if the x-api-key header is non-empty, 401 if it's missing/empty
#
# Usage: ./fake-auth-server.sh [port]

set -euo pipefail

PORT="${1:-8000}"
FIFO="$(mktemp -u /tmp/fake-auth-fifo.XXXXXX)"

cleanup() {
  rm -f "$FIFO"
}
trap cleanup EXIT INT TERM

mkfifo "$FIFO"

echo "Fake auth server listening on http://127.0.0.1:${PORT}/auth (any non-empty x-api-key -> 200)"

while true; do
  # nc's stdin is fed by $FIFO (whatever we write there gets sent to the client);
  # nc's stdout (the client's request) is piped into the handler below, whose
  # output is redirected back into $FIFO for nc to send as the response.
  nc -l "$PORT" <"$FIFO" | {
    method=""
    path=""
    apikey=""
    first_line=true

    while IFS= read -r line; do
      line="${line%$'\r'}"
      if $first_line; then
        method="${line%% *}"
        rest="${line#* }"
        path="${rest%% *}"
        first_line=false
        continue
      fi
      [[ -z "$line" ]] && break
      header_name="${line%%:*}"
      header_value="${line#*: }"
      shopt -s nocasematch
      if [[ "$header_name" == "x-api-key" ]]; then
        apikey="$header_value"
      fi
      shopt -u nocasematch
    done

    if [[ "$method" == "OPTIONS" ]]; then
      status="204 No Content"
      body=""
      extra_headers=$'Access-Control-Allow-Methods: GET, POST, OPTIONS\r\nAccess-Control-Allow-Headers: x-api-key, Content-Type\r\nAccess-Control-Max-Age: 86400\r\n'
    elif [[ "$method" == "POST" && "$path" == "/auth" ]]; then
      if [[ -n "$apikey" ]]; then
        status="200 OK"
        body='{"status":"ok"}'
      else
        status="401 Unauthorized"
        body='{"error":"missing x-api-key"}'
      fi
      extra_headers=$'Content-Type: application/json\r\n'
    else
      status="404 Not Found"
      body=""
      extra_headers=""
    fi

    printf 'HTTP/1.1 %s\r\nAccess-Control-Allow-Origin: *\r\n%sContent-Length: %d\r\nConnection: close\r\n\r\n%s' \
      "$status" "$extra_headers" "${#body}" "$body"
  } >"$FIFO"
done
