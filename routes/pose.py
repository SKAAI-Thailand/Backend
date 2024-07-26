from fastapi import APIRouter, HTTPException
from typing import Union
import database, env, security
import requests

from req_class import pose, oauth

pose_router = APIRouter()

@pose_router.get("/pose")
async def get_all_pose(
    auth_email: Union[str, None] = None,
    auth_pass: Union[str, None] = None,
    auth_token: Union[str, None] = None,
):

    user_id = None

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

    if auth_token:
        auth_url = "https://www.googleapis.com/oauth2/v3/userinfo?access_token="

        user_response = requests.get(auth_url + auth_token)
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

        cursor.execute(
            "SELECT `id` FROM `user` WHERE `email` = %s",
            (user_data.get("email"),),
        )
        result = cursor.fetchall()

        if len(result) == 0:
            return HTTPException(
                403,
                {
                    "version": env.APPLICATION.version,
                    "data": {"success": False},
                    "text": "User Not Found",
                },
            )

        user_id = result[0][0]
    elif auth_email and auth_pass:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT `id`,`password` FROM `user` WHERE `email` = %s",
            (auth_email,),
        )
        result = cursor.fetchall()

        if len(result) == 0:
            return HTTPException(
                403,
                {
                    "version": env.APPLICATION.version,
                    "data": {"success": False},
                    "text": "User Not Found",
                },
            )

        result = result[0]

        if security.Hash.check_password(auth_pass, result[1]) == False:
            return HTTPException(
                403,
                {
                    "version": env.APPLICATION.version,
                    "data": {"success": False},
                    "text": "User Not Found",
                },
            )

        user_id = result[0]

    cursor.execute("SELECT `id`, `name` FROM `pose_type`;")
    pose_type_list = cursor.fetchall()

    pose_list = {}

    for pose_type in pose_type_list:
        cursor.execute(
            "SELECT p.id, p.name, CASE WHEN EXISTS (SELECT 1 FROM pose_result pr WHERE pr.pose = p.id AND pr.accuracy >= 80 AND pr.user = %s) THEN 1 ELSE 0 END AS is_success FROM pose p WHERE p.type = %s;",
            (user_id, pose_type[0]),
        )

        pose_result = cursor.fetchall()

        if pose_result:
            pose_list[pose_type[1]] = pose_result

    return {"version": env.APPLICATION.version, "data": pose_list}


@pose_router.get("/pose/{pose_id}/info")
async def get_pose_info(pose_id: int):

    try:
        pose_id = int(pose_id)
    except ValueError:
        return HTTPException(
            400,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Invaild Pose ID",
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
        "SELECT `id`,`name`,`type`,`capture_delay`,`capture_count`,`description`,`tag` FROM `pose` WHERE `id` = %s",
        (pose_id,),
    )
    pose_info = cursor.fetchall()

    if len(pose_info) == 0:
        return HTTPException(
            401,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Pose Not Found",
            },
        )

    pose_data = pose_info[0]

    return {
        "version": env.APPLICATION.version,
        "data": {
            "id": pose_data[0],
            "name": pose_data[1],
            "type": pose_data[2],
            "capture_delay": pose_data[3],
            "capture_count": pose_data[4],
            "description": pose_data[5],
            "tag": pose_data[6],
        },
    }


@pose_router.post("/pose/{pose_id}/check")
async def check_pose_accuracy(pose_id: int, request: pose.PoseAccuracyReq):

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

    try:
        pose_id = int(pose_id)
        user_id = None

        accuracy = 10

        if request.data.auth != None:
            if isinstance(request.data.auth, oauth.GoogleOAuthData):
                auth_url = "https://www.googleapis.com/oauth2/v3/userinfo?access_token="

                user_response = requests.get(auth_url + request.data.auth.token)
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

                cursor.execute(
                    "SELECT `id` FROM `user` WHERE `email` = %s",
                    (user_data.get("email"),),
                )
                result = cursor.fetchall()

                if len(result) == 0:
                    return HTTPException(
                        403,
                        {
                            "version": env.APPLICATION.version,
                            "data": {"success": False},
                            "text": "User Not Found",
                        },
                    )

                user_id = result[0][0]

            if isinstance(request.data.auth, oauth.OAuthData):
                cursor.execute(
                    "SELECT `id`,`password` FROM `user` WHERE `email` = %s",
                    (request.data.auth.email,),
                )
                result = cursor.fetchall()

                if len(result) == 0:
                    return {
                        "version": env.APPLICATION.version,
                        "data": {
                            "success": False,
                            "text": "Account Not Found"
                        },
                    }

                result = result[0]

                if security.Hash.check_password(request.data.auth.password, result[1]) == False:
                    return {
                        "version": env.APPLICATION.version,
                        "data": {
                            "success": False,
                            "text": "Account Not Found"
                        },
                    }

                user_id = result[0]

        if user_id != None:
            cursor.execute(
                "INSERT INTO `pose_result` (`user`, `pose`, `accuracy`) VALUES (%s, %s, %s);",
                (user_id, pose_id, accuracy),
            )

        conn.commit()
        cursor.close()
        conn.close()

        return {"version": env.APPLICATION.version, "data": {"accuracy": accuracy}}

    except ValueError:
        return HTTPException(
            400,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Invaild Pose ID",
            },
        )


@pose_router.get("/pose/{pose_id}/scores")
async def get_pose_scores(
    pose_id: int,
    auth_email: str = None,
    auth_pass: str = None,
    auth_google_token: str = None,
):
    user_id = None

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

    if auth_google_token:
        auth_url = "https://www.googleapis.com/oauth2/v3/userinfo?access_token="

        user_response = requests.get(auth_url + auth_google_token)
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

        cursor.execute(
            "SELECT `id` FROM `user` WHERE `email` = %s",
            (user_data.get("email"),),
        )
        result = cursor.fetchall()

        if len(result) == 0:
            return HTTPException(
                403,
                {
                    "version": env.APPLICATION.version,
                    "data": {"success": False},
                    "text": "User Not Found",
                },
            )

        user_id = result[0][0]

    if auth_email and auth_pass:
        cursor.execute(
            "SELECT `id`,`password` FROM `user` WHERE `email` = %s",
            (auth_email,),
        )
        result = cursor.fetchall()

        if len(result) == 0:
            return {"version": env.APPLICATION.version, "data": {"success": False}}

        result = result[0]

        if security.Hash.check_password(auth_pass, result[1]) == False:
            return {"version": env.APPLICATION.version, "data": {"success": False}}

        user_id = result[0]

    if user_id == None:
        return {"success": False, "text": "OAuth Fail", "data": []}

    response_result = []

    cursor.execute(
        "SELECT `id`, `accuracy`, `timestamp` FROM `pose_result` WHERE `user` = %s AND `pose` = %s ORDER BY `timestamp` DESC LIMIT 200",
        (user_id, pose_id),
    )
    result = cursor.fetchall()

    for item in result:
        response_result.append(
            {
                "id": item[0],
                "timestamp": item[2],
                "accuracy": item[1],
            }
        )

    return {"success": True, "text": "", "data": response_result}

