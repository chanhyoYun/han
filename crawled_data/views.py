from rest_framework import status
from rest_framework.decorators import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.apps import apps
from crawled_data.generators import QuizGenerator
from crawled_data.serializers import NaverQuizSerializer, KrDictQuizSerializer


# class NaverQuizView(APIView):
# def get(self, request):
# quiz_generator = QuizGenerator(model="naver", count=10)
# quiz = quiz_generator.generate()
# serializer = NaverQuizSerializer(quiz, many=True)
# return Response(serializer.data, status=status.HTTP_200_OK)


# class KrDictQuizView(APIView):
#     def get(self, request):
#         quiz_generator = QuizGenerator(model="krdict", count=10)
#         quiz = quiz_generator.generate()
#         serializer = KrDictQuizSerializer(quiz, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)


class PuzzleCreateView(APIView):
    def get(self, request):
        quiz_generator = QuizGenerator([0, 0, 2, 0])
        quiz = quiz_generator.generator()
        # print(quiz)
        return Response(quiz)
