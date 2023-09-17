import httpx

# API CGI base path
URL_CGI = "/recepcion_datos_4.cgi"

MODEL_NAME = "Cordoba glass"

# API status operation code
API_STATUS_OP = 1002
API_STATS_OP = 1020
API_ALARMS_OP = 1079
API_SET_STATE_OP = 1013
API_SET_TEMP_OP = 1019
API_SET_POWER_OP = 1004

LOCAL_TIMEOUT = httpx.Timeout(
    # The device can be slow to respond but fast to connect to we
    # need to set a long timeout for the read and a short timeout
    # for the connect
    timeout=10.0,
    read=60.0,
)
