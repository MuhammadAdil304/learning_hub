from db_connection import db
from datetime import datetime

User = db["users"]


class UserModel:
    def __init__(self, username, email, password, role, profileImg):
        self.username = username
        self.email = email
        self.password = password
        self.profileImg = profileImg
        self.role = role
        if role == "instructor":
            self.courses = []
        if role == "student":
            self.enrolled_courses = []
        self.created_at = datetime.now()  ## pylint: disable=no-member
        self.updated_at = datetime.now()  ## pylint: disable=no-member


# Create your models here.
