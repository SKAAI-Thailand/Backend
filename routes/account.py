from email.mime.text import MIMEText
from fastapi import APIRouter, HTTPException
import database, env, security
import re, time, smtplib

from req_class import account

account_router = APIRouter()

@account_router.post("/register")
async def register_account(request: account.RegisterReq):

    if request.version != env.APPLICATION.version:
        return HTTPException(
            426,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Version Not Match",
            },
        )

    if (
        request.data.name == ""
        or request.data.email == ""
        or request.data.password == ""
    ):
        return HTTPException(
            400,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Missing Data",
            },
        )

    if not re.fullmatch(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b", request.data.email
    ):
        return HTTPException(
            400,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Invaild Email",
            },
        )

    if re.search("\s", request.data.password) or re.match(
        r"[^a-zA-Z0-9!@#$%^&*()_+.?]", request.data.password
    ):
        return HTTPException(
            400,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Invaild Password",
            },
        )

    if (
        len(request.data.password) < 8
        or not re.search("[a-z]", request.data.password)
        or not re.search("[A-Z]", request.data.password)
        or not re.search("[0-9]", request.data.password)
        or not re.search("[!@#$%^&*()_+.?]", request.data.password)
    ):
        return HTTPException(
            400,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Weak Password",
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
        "SELECT 1 FROM `user` WHERE `email` = %s",
        (request.data.email,),
    )

    if len(cursor.fetchall()) > 0:
        return HTTPException(
            403,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Email Already Exits",
            },
        )

    cursor.execute(
        "INSERT INTO `user`(`password`, `name`, `email`, `role`) VALUES (%s, %s, %s, 1)",
        (
            security.Hash.password_hash(request.data.password),
            request.data.name,
            request.data.email,
        ),
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {"version": env.APPLICATION.version, "data": {"success": True}}


@account_router.post("/reset-password")
async def reset_password(request: account.ResetPassReq):
    if request.version != env.APPLICATION.version:
        return HTTPException(
            426,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Version Not Match",
            },
        )

    if request.data.email == "":
        return HTTPException(
            400,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Missing Data",
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
        "SELECT `password` FROM `user` WHERE `email` = %s",
        (request.data.email,),
    )

    user_result = cursor.fetchall()

    if len(user_result) <= 0:
        return HTTPException(
            403,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "ไม่พบบัญชีผู้ใช้งาน",
            },
        )

    user_result = user_result[0]

    if user_result[0] == "google":
        return HTTPException(
            403,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "เข้าสู่ระบบด้วยบัญชี Google",
            },
        )

    sender_email = "" # Your Email
    sender_password = "" # Your Email Application Password
    recipient_email = request.data.email
    subject = "Reset Password"
    timestamp = str(int(time.time()))

    token = (
        recipient_email
        + "-"
        + security.Encrypt.encrypt_data(timestamp, user_result[0]).replace("-", "+")
        + "-"
        + security.Encrypt.encrypt_data(
            recipient_email + "-" + timestamp, user_result[0]
        )
    )

    reset_url = f"{{Your Frontend Domain}}/new-password?t={token}"
    privacy_policy_url = "{Your Frontend Domain}/privacy-policy.html"
    terms_of_service_url = "{Your Frontend Domain}/term-and-condition.html"

    body = f"""
<html>
<head>
<style>@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Thai+Looped&display=swap');body{{font-family:'Noto Sans Thai Looped',sans-serif;line-height:1.6;color:#333;}}h2{{color:#1a73e8;}}a:not(.button){{color:#1a73e8;text-decoration:none;}}.button{{display:inline-block;padding:10px 20px;background-color:#1a73e8;color:#fff;border-radius:5px;text-decoration:none;}}</style>
</head>
<body>
<h2>รีเซ็ตรหัสผ่าน</h2>
<p>เรียน คุณผู้ใช้งาน,</p>
<p>เราได้รับคำร้องขอให้รีเซ็ตรหัสผ่านของคุณ กรุณาคลิกที่ลิงก์ด้านล่างเพื่อรีเซ็ตรหัสผ่านของคุณ:</p>
<p style="text-align:center;"><a href="{reset_url}" class="button"style="color:#FFFFFF;">รีเซ็ตรหัสผ่าน</a></p>
<p>หากคุณไม่ได้ทำการร้องขอรีเซ็ตรหัสผ่าน กรุณาเพิกเฉยต่ออีเมลนี้หรือ <a href="{{Your Frontend Domain}}/contact">ติดต่อฝ่ายสนับสนุน</a>.</p>
<hr style="border:0;border-top:1px solid #eee;">
<p style="font-size:12px;color:#777;">ขอขอบคุณ, <br>ทีมงาน SKAAI</p>
<p style="font-size:12px;color:#777;">นโยบายความเป็นส่วนตัว: <a href="{privacy_policy_url}">อ่านเพิ่มเติม</a></p>
<p style="font-size:12px;color:#777;">ข้อตกลงการใช้งาน: <a href="{terms_of_service_url}">อ่านเพิ่มเติม</a></p>
</body>
</html>"""

    html_message = MIMEText(body, "html")
    html_message["Subject"] = subject
    html_message["From"] = sender_email
    html_message["To"] = recipient_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, recipient_email, html_message.as_string())

    return {
        "version": env.APPLICATION.version,
        "data": {"success": True},
    }


@account_router.patch("/new-password")
async def new_password(request: account.NewPassReq):

    if request.version != env.APPLICATION.version:
        return HTTPException(
            426,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Version Not Match",
            },
        )

    password_errors = []

    if len(request.data.password) < 8:
        password_errors.append("รหัสผ่านต้องมีความยาวอย่างน้อย 8 ตัวอักษร")
    if not re.search("[a-z]", request.data.password):
        password_errors.append("รหัสผ่านต้องมีตัวอักษรพิมพ์เล็กอย่างน้อย 1 ตัว")
    if not re.search("[A-Z]", request.data.password):
        password_errors.append("รหัสผ่านต้องมีตัวอักษรพิมพ์ใหญ่อย่างน้อย 1 ตัว")
    if not re.search("[0-9]", request.data.password):
        password_errors.append("รหัสผ่านต้องมีตัวเลขอย่างน้อย 1 ตัว")
    if not re.search("[!@#$%^&*()_+.?]", request.data.password):
        password_errors.append("รหัสผ่านต้องมีสัญลักษณ์พิเศษอย่างน้อย 1 ตัว")

    if len(password_errors) > 0:
        return HTTPException(
            400,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "รหัสผ่านอ่อนแอ: " + ",\n".join(password_errors),
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

    spilt_part_token = request.data.token.split("-")
    email = spilt_part_token[0]
    enc_timestamp = spilt_part_token[1].replace("+", "-")
    enc_secret = "-".join(spilt_part_token[2:])

    cursor = conn.cursor()
    cursor.execute(
        "SELECT `password` FROM `user` WHERE `email` = %s",
        (email,),
    )

    user_result = cursor.fetchall()

    if len(user_result) <= 0:
        return HTTPException(
            403,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Token ไม่ถูกต้อง",
            },
        )

    user_old_password = user_result[0][0]

    raw_timestamp = security.Encrypt.decrypt_data(enc_timestamp, user_old_password)

    if raw_timestamp == False:
        return HTTPException(
            403,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Token ไม่ถูกต้อง",
            },
        )

    if int(time.time()) - int(raw_timestamp) >= 60 * 5:
        return HTTPException(
            403,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Token หมดอายุ",
            },
        )

    plantext_secret = security.Encrypt.decrypt_data(enc_secret, user_old_password)

    if plantext_secret == False:
        return HTTPException(
            403,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Token ไม่ถูกต้อง1: " + enc_secret,
            },
        )

    if plantext_secret != email + "-" + raw_timestamp:
        return HTTPException(
            403,
            {
                "version": env.APPLICATION.version,
                "data": {"success": False},
                "text": "Token ไม่ถูกต้อง2",
            },
        )

    cursor.execute(
        "UPDATE `user` SET `password` = %s WHERE `email` = %s;",
        (security.Hash.password_hash(request.data.password), email),
    )

    conn.commit()
    cursor.close()
    conn.close()

    return {"version": env.APPLICATION.version, "data": {"success": True}}
