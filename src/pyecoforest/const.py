import httpx

# API CGI base path
URL_CGI = "/recepcion_datos_4.cgi"

# API status operation code
API_STATUS_OP = 1002

LOCAL_TIMEOUT = httpx.Timeout(
    # The device can be slow to respond but fast to connect to we
    # need to set a long timeout for the read and a short timeout
    # for the connect
    timeout=10.0,
    read=60.0,
)
