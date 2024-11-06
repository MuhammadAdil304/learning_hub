from db_connection import db
from datetime import datetime

Courses = db["courses"]


class CourseModel:
    def __init__(self, title, desc, userId):
        self.title = title
        self.desc = desc
        self.userId = userId
        self.modules = []
        self.reviews = []
        self.status = False
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
