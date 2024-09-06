from litestar.security.session_auth import SessionAuth

s = SessionAuth()
s.on_app_init