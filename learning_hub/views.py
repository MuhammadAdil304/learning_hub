from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models.userModels import User, UserModel
from .models.courseModels import CourseModel, Courses
from datetime import datetime, timedelta
from bson import ObjectId
import json
import jwt


@csrf_exempt
def Signup(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            username = data.get("username")
            email = data.get("email")
            role = data.get("role")
            password = data.get("password")

            if not username or not email or not password or not role:
                return JsonResponse({"error": "All Fields are required"}, status=401)

            check_user = User.find_one({"email": email})
            if check_user:
                return JsonResponse({"error": "Email already exists"}, status=401)

            new_user = UserModel(username, email, password, role)
            User.insert_one(new_user.__dict__)
            return JsonResponse(
                {
                    "message": "User Created Successfully",
                    "user": {
                        "username": new_user.username,
                        "email": new_user.email,
                        "role": new_user.role,
                        "created_at": new_user.created_at,
                        "updated_at": new_user.updated_at,
                    },
                },
                status=200,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=300)
    else:
        return HttpResponse("<p>Invalid request method</p>")


@csrf_exempt
def Login(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return JsonResponse({"error": "All Fields are required"}, status=401)

            user_exist = User.find_one({"email": email, "password": password})
            if not user_exist:
                return JsonResponse({"error": "Invalid credentials"}, status=401)
            payload = {
                "user_id": str(user_exist["_id"]),
                "email": user_exist["email"],
                "exp": datetime.now() + timedelta(hours=24),
            }
            access_token = jwt.encode(payload, "AdilLMS", algorithm="HS256")
            user_info = {
                "id": str(user_exist["_id"]),
                "username": user_exist["username"],
                "email": user_exist["email"],
                "role": user_exist["role"],
                "courses": [str(ObjectId) for ObjectId in user_exist["courses"]],
                "access_token": access_token,
            }
            return JsonResponse(
                {"message": "Login Successfully", "user": user_info}, status=200
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    else:
        return HttpResponse("<p>Invalid request method</p>")


def token_required(func):
    def wrapper(request, *args, **kwargs):
        access_token = request.headers.get("Authorization")
        if not access_token:
            return JsonResponse({"error": "Token is missing"}, status=401)
        try:
            payload = jwt.decode(access_token, "AdilLMS", algorithms=["HS256"])
            user_id = payload["user_id"]
            user_exist = User.find_one({"_id": ObjectId(user_id)})
            if not user_exist:
                return JsonResponse({"error": "Invalid token"}, status=401)
            return func(request, *args, **kwargs)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=401)

    return wrapper


@csrf_exempt
@token_required
def Create_course(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            user_id = request.headers.get("userId")
            title = data.get("title")
            desc = data.get("desc")
            if not title or not desc:
                return JsonResponse({"error": "All Fields are required"}, status=401)
            title_exist = Courses.find_one({"title": title})
            if title_exist:
                return JsonResponse({"error": "Title already exists"}, status=401)
            new_course = CourseModel(title, desc, user_id)
            inserted_course = Courses.insert_one(new_course.__dict__)
            course_id = inserted_course.inserted_id
            print(course_id)
            User.update_one(
                {"_id": ObjectId(user_id), "role": "instructor"},
                {"$push": {"courses": course_id}},
            )
            return JsonResponse(
                {
                    "message": "Course Created Successfully",
                },
                status=200,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("<p>Invalid request method</p>")


@csrf_exempt
@token_required
def Create_module(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            course_id = request.headers.get("courseId")
            title = data.get("title")
            content = data.get("content")
            if not title or not content:
                return JsonResponse({"error": "All Fields are required"}, status=401)
            title_exist = Courses.find_one(
                {"_id": ObjectId(course_id), "modules.title": title}
            )
            if title_exist:
                return JsonResponse({"error": "Title already exists"}, status=401)
            new_module = {
                "module_id": str(ObjectId()),
                "title": title,
                "content": content,
                "lessons": [],
                "quizzes": [],
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
            Courses.update_one(
                {"_id": ObjectId(course_id)}, {"$push": {"modules": new_module}}
            )
            Courses.update_one({"_id": ObjectId(course_id)}, {"$set": {"status": True}})
            return JsonResponse(
                {"message": "Lesson created successfully", "module": new_module},
                status=200,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("<p>Invalid request method</p>")


@csrf_exempt
@token_required
def Create_lesson(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            course_id = request.headers.get("courseId")
            module_id = request.headers.get("moduleId")
            title = data.get("title")
            content = data.get("content")
            if not title or not content:
                return JsonResponse({"error": "All Fields are required"}, status=401)
            title_exist = Courses.find_one(
                {
                    "_id": ObjectId(course_id),
                    "modules.module_id": module_id,
                    "modules.lessons.title": title,
                }
            )
            if title_exist:
                return JsonResponse({"error": "Title already exists"}, status=401)
            new_lesson = {
                "lesson_id": str(ObjectId()),
                "title": title,
                "content": content,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
            print("module_id", module_id)
            print("course_id", course_id)
            Courses.update_one(
                {"_id": ObjectId(course_id), "modules.module_id": module_id},
                {"$push": {"modules.$.lessons": new_lesson}},
            )
            return JsonResponse(
                {"message": "Lesson created successfully", "lesson": new_lesson},
                status=200,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("<p>Invalid request method</p>")


@csrf_exempt
@token_required
def Create_quiz(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            course_id = request.headers.get("courseId")
            module_id = request.headers.get("moduleId")
            title = data.get("title")
            questions = data.get("questions", [])
            if not title or not questions:
                return JsonResponse({"error": "All fields are required"}, status=401)
            title_exist = Courses.find_one(
                {
                    "_id": ObjectId(course_id),
                    "modules.module_id": module_id,
                    "modules.quizzes.title": title,
                }
            )
            if title_exist:
                return JsonResponse({"error": "Title already exists"}, status=401)
            formated_questions = []
            for question in questions:
                formated_questions.append(
                    {
                        "question_id": str(ObjectId()),
                        "question": question["question"],
                        "options": question.get("options", []),
                        "answer": question["answer"],
                    }
                )
            new_quiz = {
                "quiz_id": str(ObjectId()),
                "title": title,
                "questions": formated_questions,
                "created_at": datetime.now(),
                "updated_at": datetime.now(),
            }
            print("module_id", module_id)
            print("course_id", course_id)
            Courses.update_one(
                {"_id": ObjectId(course_id), "modules.module_id": module_id},
                {"$push": {"modules.$.quizzes": new_quiz}},
            )
            return JsonResponse(
                {"message": "Quiz created successfully", "quiz": new_quiz},
                status=200,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("<p>Invalid request method</p>")


@csrf_exempt
@token_required
def Update_course(request, courseId):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            title = data.get("title")
            desc = data.get("desc")
            if not title or not desc:
                return JsonResponse({"error": "All fields are required"}, status=401)
            Courses.update_one(
                {"_id": ObjectId(courseId)}, {"$set": {"title": title, "desc": desc}}
            )
            return JsonResponse(
                {
                    "message": "Course updated successfully",
                },
                status=200,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("<p>Invalid request method</p>")


@csrf_exempt
@token_required
def Delete_course(request, courseId):
    if request.method == "DELETE":
        try:
            Courses.delete_one({"_id": ObjectId(courseId)})
            return JsonResponse({"message": "Course deleted successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("<p>Invalid request method</p>")


@csrf_exempt
@token_required
def Delete_lesson(request, lessonId):
    if request.method == "DELETE":
        try:
            Courses.update_one(
                {
                    "modules.lessons.lesson_id": lessonId,
                },
                {"$pull": {"modules.$.lessons": {"lesson_id": lessonId}}},
            )
            return JsonResponse({"message": "Lesson deleted successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("<p>Invalid request method</p>")


@csrf_exempt
@token_required
def Delete_module(request, moduleId):
    if request.method == "DELETE":
        try:
            Courses.update_one(
                {"modules.module_id": moduleId},
                {"$pull": {"modules": {"module_id": moduleId}}},
            )
            return JsonResponse({"message": "Module deleted successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("<p>Invalid request method</p>")


@csrf_exempt
@token_required
def Delete_quiz(request, quizId):
    if request.method == "DELETE":
        try:
            Courses.update_one(
                {"modules.quizzes.quiz_id": quizId},
                {"$pull": {"modules.$.quizzes": {"quiz_id": quizId}}},
            )
            return JsonResponse({"message": "Quiz deleted successfully"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("<p>Invalid request method</p>")


def Get_all_courses(request):
    if request.method == "GET":
        try:
            course_list = []
            for course in Courses.find():

                course_list.append(
                    {
                        "id": str(course["_id"]),
                        "userId": course["userId"],
                        "title": course["title"],
                        "desc": course["desc"],
                        "modules": course["modules"],
                        "reviews": course["reviews"],
                        "status": course["status"],
                    }
                )
            return JsonResponse({"courses": course_list}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("<p>Invalid request method</p>")


@token_required
def Get_course_by_user(request, userId):
    if request.method == "GET":
        try:
            courses = Courses.find({"userId": userId})
            courseList = []
            for course in courses:
                courseList.append(
                    {
                        "id": str(course["_id"]),
                        "title": course["title"],
                        "desc": course["desc"],
                        "modules": course["modules"],
                        "status": course["status"],
                    }
                )
            return JsonResponse({"courses": courseList}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("<p>Invalid request method</p>")


def Get_course_by_id(request, courseId):
    if request.method == "GET":
        try:
            course = Courses.find_one({"_id": ObjectId(courseId)})
            if course:
                return JsonResponse(
                    {
                        "id": str(course["_id"]),
                        "title": course["title"],
                        "desc": course["desc"],
                        "modules": course["modules"],
                        "status": course["status"],
                    },
                    status=200,
                )
            return JsonResponse({"error": "Course not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
    return HttpResponse("<p>Invalid request method</p>")
