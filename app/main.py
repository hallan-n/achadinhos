import uvicorn
from database.schemas import Session
from fastapi import FastAPI
from routes.login import route as login
from webbot import get_login_session, publish_post

app = FastAPI()

app.include_router(login)


@app.get("/")
async def mds():
    # session = await get_login_session({"role": "instagram","id":10,"user": "achadinhozdaily", "password": "Tango@135799"})
    session = Session(
        state={
            "cookies": [
                {
                    "name": "csrftoken",
                    "value": "efx43iKb54VE9AgntAhAK5",
                    "domain": ".instagram.com",
                    "path": "/",
                    "expires": 1784837393.607718,
                    "httpOnly": False,
                    "secure": True,
                    "sameSite": "Lax",
                },
                {
                    "name": "datr",
                    "value": "Cx1TaP3u3AE6OGyB9W5Ec2_l",
                    "domain": ".instagram.com",
                    "path": "/",
                    "expires": 1784837387.831757,
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "None",
                },
                {
                    "name": "ig_did",
                    "value": "DFCBBAE6-08B7-4C39-935A-7A870FD7A570",
                    "domain": ".instagram.com",
                    "path": "/",
                    "expires": 1781813392.4598,
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "Lax",
                },
                {
                    "name": "wd",
                    "value": "1280x720",
                    "domain": ".instagram.com",
                    "path": "/",
                    "expires": 1750882193,
                    "httpOnly": False,
                    "secure": True,
                    "sameSite": "Lax",
                },
                {
                    "name": "mid",
                    "value": "aFMdCwALAAGHFLfBJY2Dw9pT_aB3",
                    "domain": ".instagram.com",
                    "path": "/",
                    "expires": 1784837388,
                    "httpOnly": False,
                    "secure": True,
                    "sameSite": "Lax",
                },
                {
                    "name": "sessionid",
                    "value": "75287931192%3AuV0J6vcIVNfOUI%3A5%3AAYc2kRhQX-jaQsDAxk8axSnaGqOGug-dH4gYVVyqvg",
                    "domain": ".instagram.com",
                    "path": "/",
                    "expires": 1781813392.459508,
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "Lax",
                },
                {
                    "name": "ds_user_id",
                    "value": "75287931192",
                    "domain": ".instagram.com",
                    "path": "/",
                    "expires": 1758053393.607791,
                    "httpOnly": False,
                    "secure": True,
                    "sameSite": "None",
                },
                {
                    "name": "rur",
                    "value": '"VLL\\05475287931192\\0541781813393:01febe1e4abb097a1975a1a32db9fe14fe8159144afbacf18258174e7879b836f583e0e8"',
                    "domain": ".instagram.com",
                    "path": "/",
                    "expires": -1,
                    "httpOnly": True,
                    "secure": True,
                    "sameSite": "Lax",
                },
            ],
            "origins": [
                {
                    "origin": "https://www.instagram.com",
                    "localStorage": [
                        {
                            "name": "chatd-deviceid",
                            "value": "8d13fe4a-ce6b-441d-8073-bd91eba78093",
                        },
                        {
                            "name": "ig_boost_inline_ads_tooltip",
                            "value": '{"count":0,"lastSeen":1749672593223}',
                        },
                        {"name": "hb_timestamp", "value": "1750277388645"},
                        {"name": "IGSession", "value": "j4t1sh:1750279193350"},
                        {"name": "pigeon_state", "value": '{"lastDeviceInfoTime":0}'},
                        {"name": "signal_flush_timestamp", "value": "1750277388666"},
                        {"name": "Session", "value": "vczah2:1750277428350"},
                        {
                            "name": "has_interop_upgraded",
                            "value": '{"lastCheckedAt":1750277393646,"status":false}',
                        },
                        {
                            "name": "banzai:last_storage_flush",
                            "value": "1750277389360.8",
                        },
                    ],
                }
            ],
        },
        cookies=[
            {
                "name": "csrftoken",
                "value": "efx43iKb54VE9AgntAhAK5",
                "domain": ".instagram.com",
                "path": "/",
                "expires": 1784837393.789681,
                "httpOnly": False,
                "secure": True,
                "sameSite": "Lax",
            },
            {
                "name": "datr",
                "value": "Cx1TaP3u3AE6OGyB9W5Ec2_l",
                "domain": ".instagram.com",
                "path": "/",
                "expires": 1784837387.831757,
                "httpOnly": True,
                "secure": True,
                "sameSite": "None",
            },
            {
                "name": "ig_did",
                "value": "DFCBBAE6-08B7-4C39-935A-7A870FD7A570",
                "domain": ".instagram.com",
                "path": "/",
                "expires": 1781813392.4598,
                "httpOnly": True,
                "secure": True,
                "sameSite": "Lax",
            },
            {
                "name": "wd",
                "value": "1280x720",
                "domain": ".instagram.com",
                "path": "/",
                "expires": 1750882193,
                "httpOnly": False,
                "secure": True,
                "sameSite": "Lax",
            },
            {
                "name": "mid",
                "value": "aFMdCwALAAGHFLfBJY2Dw9pT_aB3",
                "domain": ".instagram.com",
                "path": "/",
                "expires": 1784837388,
                "httpOnly": False,
                "secure": True,
                "sameSite": "Lax",
            },
            {
                "name": "sessionid",
                "value": "75287931192%3AuV0J6vcIVNfOUI%3A5%3AAYc2kRhQX-jaQsDAxk8axSnaGqOGug-dH4gYVVyqvg",
                "domain": ".instagram.com",
                "path": "/",
                "expires": 1781813392.459508,
                "httpOnly": True,
                "secure": True,
                "sameSite": "Lax",
            },
            {
                "name": "ds_user_id",
                "value": "75287931192",
                "domain": ".instagram.com",
                "path": "/",
                "expires": 1758053393.789726,
                "httpOnly": False,
                "secure": True,
                "sameSite": "None",
            },
            {
                "name": "rur",
                "value": '"VLL\\05475287931192\\0541781813393:01febe1e4abb097a1975a1a32db9fe14fe8159144afbacf18258174e7879b836f583e0e8"',
                "domain": ".instagram.com",
                "path": "/",
                "expires": -1,
                "httpOnly": True,
                "secure": True,
                "sameSite": "Lax",
            },
        ],
        local_storage={
            "chatd-deviceid": "8d13fe4a-ce6b-441d-8073-bd91eba78093",
            "ig_boost_inline_ads_tooltip": '{"count":0,"lastSeen":1749672593223}',
            "hb_timestamp": "1750277388645",
            "IGSession": "j4t1sh:1750279193350",
            "pigeon_state": '{"lastDeviceInfoTime":0}',
            "signal_flush_timestamp": "1750277388666",
            "Session": "vczah2:1750277428350",
            "has_interop_upgraded": '{"lastCheckedAt":1750277393827,"status":false}',
            "banzai:last_storage_flush": "1750277389360.8",
        },
        session_storage={
            "original_referrer": "",
            "IGTabId": "t2yde0",
            "TabId": "sl2o2t",
            "www-claim-v2": "hmac.AR20yLtmqIsUkCpz0kUDG6UT5g7xULZd9rs4IOHok6Iz0CVV",
            "pigeon_state": '{"lastEventTime":1750277392477,"sequenceID":0,"sessionID":"19784a97842-ba4151"}',
        },
        login_at="2025-06-18T17:09:53.900095",
        login_id=10,
    )
    await publish_post(session)


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", reload=True)
