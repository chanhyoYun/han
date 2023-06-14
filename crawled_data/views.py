from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.apps import apps


from crawled_data.models import NaverQuiz, KrDictQuiz
from crawled_data.generators import QuizGenerator
from crawled_data.serializers import NaverQuizSerializer, KrDictQuizSerializer


class NaverQuizView(APIView):
    def get(self, request):
        quiz = QuizGenerator.generate(NaverQuiz)
        serializer = NaverQuizSerializer(quiz, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class KrDictQuizView(APIView):
    def get(self, request):
        quiz = QuizGenerator.generate(KrDictQuiz)
        serializer = KrDictQuizSerializer(quiz, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
