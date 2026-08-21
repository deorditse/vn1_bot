# Generate description proxy

`POST /generate-description` is an authenticated, documented binary proxy to the generator endpoint with the same path. The gateway forwards JSON or multipart bodies and trusted user headers, then preserves the upstream status, content type, content disposition, and response bytes. Upstream connection failures use the existing gateway 502 error response.
