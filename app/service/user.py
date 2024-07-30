import random
import smtplib
import time
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import bcrypt
import jwt


class UserService:
    encoding = "UTF-8"
    secret_key = "134a51d7bdac45cc59924cbb10ba53c59bf333cff65625961e7421c03700fb4c"
    jwt_algorithm = "HS256"

    def hash_password(self, plain_password: str) -> str:
        hashed_password: bytes = bcrypt.hashpw(plain_password.encode(self.encoding), salt=bcrypt.gensalt())
        return hashed_password.decode(self.encoding)

    def varify_password(self, plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode(self.encoding), hashed_password.encode(self.encoding))

    def create_jwt(self, email: str) -> str:
        # sub -> 식별자, exp -> 만료시간
        return jwt.encode(
            payload={"sub": email, "exp": datetime.utcnow() + timedelta(days=1)},
            key=self.secret_key,
            algorithm=self.jwt_algorithm
        )

    def decode_jwt(self, access_token: str):
        payload = jwt.decode(access_token, key=self.secret_key, algorithms=[self.jwt_algorithm])
        return payload["sub"]

    @staticmethod
    def create_otp() -> int:
        return random.randint(1000, 9999)

    @staticmethod
    def send_email_to_user(email: str, otp : int) -> None:
        sender_email = "kimal846@naver.com"
        sender_password = "R21QTJQD8EBR"

        message = MIMEMultipart("alternative")
        message["Subject"] = "이메일 인증입니다."
        message["From"] = sender_email
        message["To"] = email

        text = f"Your OTP code is {otp}"
        html = f"""\
        <html>
            <body>
                <p>Your OTP code is <strong>{otp}</strong></p>
            </body>
        </html>
        """

        part1 = MIMEText(text, "plain")
        part2 = MIMEText(html, "html")

        message.attach(part1)
        message.attach(part2)

        time.sleep(5)

        with smtplib.SMTP_SSL("smtp.naver.com", 465) as server:
            server.login(user=sender_email, password=sender_password)
            server.sendmail(from_addr=sender_email, to_addrs=email, msg=message.as_string())
