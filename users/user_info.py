from rest_framework.generics import get_object_or_404
from users.models import User, UserInfo
from users.serializers import UserSerializer
from datetime import datetime, timedelta


def check_user_info(serializer, user_id):
    """변경되는 유저정보 확인 함수

    유저레벨, 경험치, 학습일수, 연속학습일 수 반영

    """
    user = get_object_or_404(User, pk=user_id)
    user_info = get_object_or_404(UserInfo, player_id=user_id)

    # 유저 경험치 반영
    solved_quizzes = [x for x in serializer if x["solved"]]
    earn_exp = 10 * len(solved_quizzes)
    user_info.experiment += earn_exp

    if user_info.experiment >= user_info.max_experiment:
        user_info.level += 1
        user_info.experiment -= user_info.max_experiment
        user_info.max_experiment += (user_info.level - 1) * 10

    # 유저 푼 문제 갯수 카운터
    user_info.quizzes_count += len(solved_quizzes)

    # 유저 학습일수, 연속 학습일수 반영
    today = datetime.now()
    last_login_date = datetime.strptime(str(user.last_login.date()), "%Y-%m-%d")
    attend_date = datetime.strptime(str(user_info.attend.date()), "%Y-%m-%d")

    user_attend = last_login_date - attend_date

    if user_attend.days == 1:
        user_info.day += 1
    else:
        user_info.day = 1

    # 정상 학습시, 학습 시작일 오늘로 설정.
    if attend_date != last_login_date:
        user_info.total_study_day += 1
        user_info.attend = today

    user_info.save()

    # 저장된 유저정보에 따른 칭호 지급 확인
    check_achieve(user_id)


def check_achieve(user_id):
    """칭호 지급 함수

    각 칭호 지급 조건에 따른 칭호 지급

    """
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


def user_quiz_pass_update(user_id):
    """유저 퀴즈 통과 시 작동되는 함수

    UserInfo의 경험치를 업데이트 할 때 사용

    """
    user_info = get_object_or_404(UserInfo, player_id=user_id)

    # 유저 경험치 반영
    earn_exp = 50
    user_info.experiment += earn_exp

    if user_info.experiment >= user_info.max_experiment:
        user_info.level += 1
        user_info.experiment -= user_info.max_experiment
        user_info.max_experiment += (user_info.level - 1) * 10

    user_info.save()

    # 저장된 유저정보에 따른 칭호 지급 확인
    check_achieve(user_id)
