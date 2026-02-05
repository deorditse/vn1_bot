import httpx

VPN_PROXY = "socks5h://xray:10808"

client_httpx_vpn = httpx.Client(
    proxy=VPN_PROXY,
    timeout=60,
)

client_httpx = httpx.Client(
    timeout=30,
)
