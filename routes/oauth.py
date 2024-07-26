from fastapi import APIRouter, HTTPException
import database, env, security
import requests

from req_class import oauth

oauth_router = APIRouter()

@oauth_router.post("/oauth")
async def api_oauth(request: oauth.OAuthReq):

    if request.version != env.APPLICATION.version:
        return HTTPException(
            426,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Version Not Match",
            },
        )

    conn = database.Connect()

    if conn == False:
        return HTTPException(
            500,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Database Connect Fail",
            },
        )

    cursor = conn.cursor()
    cursor.execute(
        "SELECT `id`,`name`,`role`,`password` FROM `user` WHERE `email` = %s",
        (request.data.email,),
    )
    result = cursor.fetchall()

    if len(result) == 0:
        return {"version": env.APPLICATION.version, "data": {"success": False}}

    result = result[0]

    if security.Hash.check_password(request.data.password, result[3]) == False:
        return {
            "version": env.APPLICATION.version,
            "data": {"success": False, "d1": result[3], "d2": request.data.password},
        }

    return {
        "version": env.APPLICATION.version,
        "data": {
            "success": True,
            "id": result[0],
            "name": result[1],
            "role": result[2],
        },
    }


@oauth_router.get("/oauth-url/google")
async def get_google_url():
    return {
        "url": f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={env.GOOGLE.CLIENT_ID}&redirect_uri={env.GOOGLE.REDIRECT_URI[0]}&scope=https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email&prompt=select_account"
    }


@oauth_router.get("/oauth-url/pwa-google")
async def get_google_url():
    return {
        "url": f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={env.GOOGLE.CLIENT_ID}&redirect_uri={env.GOOGLE.REDIRECT_URI[1]}&scope=https://www.googleapis.com/auth/userinfo.profile https://www.googleapis.com/auth/userinfo.email&prompt=select_account"
    }


@oauth_router.post("/oauth/google-code")
async def auth_google_code(request: oauth.GoogleOAuthCodeReq):

    if request.version != env.APPLICATION.version:
        return HTTPException(
            426,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Version Not Match",
            },
        )

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": request.data.code,
        "client_id": env.GOOGLE.CLIENT_ID,
        "client_secret": env.GOOGLE.CLIENT_SECRET,
        "redirect_uri": env.GOOGLE.REDIRECT_URI[0],
        "grant_type": "authorization_code",
    }

    token_response = requests.post(token_url, data=data)
    token_data = token_response.json()

    if token_data.get("error") != None:
        return HTTPException(
            400,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Invaild Code",
            },
        )

    access_token = token_data.get("access_token")

    auth_url = "https://www.googleapis.com/oauth2/v3/userinfo?access_token="

    user_response = requests.get(auth_url + access_token)
    user_data = user_response.json()

    if user_data.get("error") != None:
        return HTTPException(
            400,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Invaild Token",
            },
        )

    conn = database.Connect()

    if conn == False:
        return HTTPException(
            500,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Database Connect Fail",
            },
        )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT `id`,`name`,`role` FROM `user` WHERE `email` = %s",
        (user_data.get("email"),),
    )
    result = cursor.fetchall()

    if len(result) > 0:
        result = result[0]
        return {
            "version": env.APPLICATION.version,
            "data": {
                "success": True,
                "token": access_token,
                "id": result[0],
                "name": result[1],
                "role": result[2],
            },
        }

    cursor.execute(
        "INSERT INTO `user`(`password`, `name`, `email`, `role`) VALUES ('google', %s, %s, 1)",
        (
            user_data.get("name"),
            user_data.get("email"),
        ),
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "version": env.APPLICATION.version,
        "data": {
            "success": True,
            "token": access_token,
            "id": cursor.lastrowid,
            "name": user_data.get("name"),
            "role": 1,
        },
    }


@oauth_router.post("/oauth/pwa-google-code")
async def auth_google_code(request: oauth.GoogleOAuthCodeReq):

    if request.version != env.APPLICATION.version:
        return HTTPException(
            426,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Version Not Match",
            },
        )

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": request.data.code,
        "client_id": env.GOOGLE.CLIENT_ID,
        "client_secret": env.GOOGLE.CLIENT_SECRET,
        "redirect_uri": env.GOOGLE.REDIRECT_URI[1],
        "grant_type": "authorization_code",
    }

    token_response = requests.post(token_url, data=data)
    token_data = token_response.json()

    if token_data.get("error") != None:
        return HTTPException(
            400,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Invaild Code",
            },
        )

    access_token = token_data.get("access_token")

    auth_url = "https://www.googleapis.com/oauth2/v3/userinfo?access_token="

    user_response = requests.get(auth_url + access_token)
    user_data = user_response.json()

    if user_data.get("error") != None:
        return HTTPException(
            400,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Invaild Token",
            },
        )

    conn = database.Connect()

    if conn == False:
        return HTTPException(
            500,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Database Connect Fail",
            },
        )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT `id`,`name`,`role` FROM `user` WHERE `email` = %s",
        (user_data.get("email"),),
    )
    result = cursor.fetchall()

    if len(result) > 0:
        result = result[0]
        return {
            "version": env.APPLICATION.version,
            "data": {
                "success": True,
                "token": access_token,
                "id": result[0],
                "name": result[1],
                "role": result[2],
            },
        }

    cursor.execute(
        "INSERT INTO `user`(`password`, `name`, `email`, `role`) VALUES ('google', %s, %s, 1)",
        (
            user_data.get("name"),
            user_data.get("email"),
        ),
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {
        "version": env.APPLICATION.version,
        "data": {
            "success": True,
            "token": access_token,
            "id": cursor.lastrowid,
            "name": user_data.get("name"),
            "role": 1,
        },
    }


@oauth_router.post("/oauth/google")
async def auth_google(request: oauth.GoogleOAuthReq):

    if request.version != env.APPLICATION.version:
        return HTTPException(
            426,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Version Not Match",
            },
        )

    access_token = request.data.token

    auth_url = "https://www.googleapis.com/oauth2/v3/userinfo?access_token="

    user_response = requests.get(auth_url + access_token)
    user_data = user_response.json()

    if user_data.get("error") != None:
        return HTTPException(
            400,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Invaild Token",
            },
        )

    conn = database.Connect()

    if conn == False:
        return HTTPException(
            500,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Database Connect Fail",
            },
        )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT `id`,`name`,`role` FROM `user` WHERE `email` = %s",
        (user_data.get("email"),),
    )
    result = cursor.fetchall()

    if len(result) > 0:
        result = result[0]
        return {
            "version": env.APPLICATION.version,
            "data": {
                "success": True,
                "token": access_token,
                "id": result[0],
                "name": result[1],
                "role": result[2],
            },
        }

    return HTTPException(
        403,
        {
            "version": env.APPLICATION.version,
            "data": {"success": False},
            "text": "User Not Found",
        },
    )