import httpx
import os
from litestar.testing import TestClient

os.environ.setdefault("FIMBU_SETTINGS_MODULE", "Tst.settings")

from fimbu.conf import settings

settings.DEBUG = False

from Tst.main import application




with httpx.Client(base_url="http://127.0.0.1:8000") as client:
    response = client.post("/auth/login", json={
        "email": "user@example.com", 
        "password": "string"
    })

    
    assert response.status_code == 201, "Login must return 201"
    crsf_token = response.cookies['csrftoken']

    my_profile = client.get("/auth/profile", headers={"x-csrftoken": crsf_token})
    assert my_profile.json()['email'] == 'user@example.com'

    
    update_my_profile = client.patch("/auth/profile", json={
        "avatar_url": "https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png",
    }, headers={"x-csrftoken": crsf_token})

    print(update_my_profile.status_code, update_my_profile.content)
    assert update_my_profile.json()['avatar_url'] == 'https://www.google.com/images/branding/googlelogo/2x/googlelogo_color_272x92dp.png'

