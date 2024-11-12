from django.urls import path
from .views import *  ## pylint: disable=import-error

urlpatterns = [
    path("sign-up/", Signup, name="signup"),
    path("login/", Login, name="login"),
    path("create-course/", Create_course, name="createcourse"),
    path("create-module/", Create_module, name="createmodule"),
    path("create-lesson/", Create_lesson, name="createlesson"),
    path("create-quiz/", Create_quiz, name="createquiz"),
    path("get-all-courses/", Get_all_courses, name="getallcourses"),
    path("update-course/<courseId>", Update_course, name="updatecourse"),
    path("delete-course/<courseId>", Delete_course, name="deletecourse"),
    path("delete-lesson/<lessonId>", Delete_lesson, name="deletelesson"),
    path("delete-quiz/<quizId>", Delete_quiz, name="deletequiz"),
    path("delete-module/<moduleId>", Delete_module, name="deletemodule"),
    path("get-course-by-id/<courseId>", Get_course_by_id, name="getcoursebyid"),
    path("get-courses-by-userId/<userId>", Get_course_by_user, name="getcoursebyuserid"),
    path("get-user-by-id/", get_user_by_id, name="getuserbyid"),
]
