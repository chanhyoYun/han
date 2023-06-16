from rest_framework.generics import get_object_or_404
from users.models import User, UserInfo
from users.serializers import UserSerializer
from datetime import datetime


def check_user_info(serializer, user_id):
    user = get_object_or_404(User, pk=user_id)
    user_info = get_object_or_404(UserInfo, player_id=user_id)

    solved_quizzes = [x for x in serializer if x["solved"]]
    earn_exp = 10 * len(solved_quizzes)
    user_info.experiment += earn_exp

    user_info.quizzes_count += len(solved_quizzes)

    if user_info.experiment >= user_info.max_experiment:
        user_info.level += 1
        user_info.experiment -= user_info.max_experiment
        user_info.max_experiment += (user_info.level - 1) * 10

    user_attend = str(user_info.attend).split(" ")[0]
    user_last_login = str(user.last_login).split(" ")[0]
    today = datetime.now()

    if int(user_last_login.split("-")[2]) - int(user_attend.split("-")[2]) == 1:
        user_info.day += 1
    elif int(user_last_login.split("-")[2]) - int(user_attend.split("-")[2]) != 0:
        user_info.day = 1

    if user_attend != user_last_login:
        user_info.attend = today

    user_info.save()
    check_achieve(user_id)


def check_achieve(user_id):
    user = get_object_or_404(User, pk=user_id)
    serializer = UserSerializer(user)
    user_info = get_object_or_404(UserInfo, player_id=user_id)
    # 레벨 유형별 칭호 지급
    if user_info.level == 3:
        user.achieve.add(1)
    if user_info.level == 5:
        user.achieve.add(2)
    if user_info.level == 10:
        user.achieve.add(3)

    # 친구 유형별 칭호 지급
    if len(serializer.data["followings"]) >= 5:
        user.achieve.add(4)

    # 출석 유형별 칭호 지급
    if user_info.day == 3:
        user.achieve.add(5)
    if user_info.day == 5:
        user.achieve.add(6)
    if user_info.day == 10:
        user.achieve.add(7)

    # 푼 문제 유형 별 칭호 지급
    if user_info.quizzes_count >= 20:
        user.achieve.add(8)
    if user_info.quizzes_count >= 50:
        user.achieve.add(9)
    if user_info.quizzes_count >= 100:
        user.achieve.add(10)
