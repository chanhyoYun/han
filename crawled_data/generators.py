from crawled_data.models import NaverQuiz, KrDictQuiz, KrDictQuizExplain
from crawled_data.serializers import (
    NaverQuizSerializer,
    KrDictQuizSerializer,
    FillInTheBlankSerializer,
)
import random
import numpy as np
import re
from kiwipiepy import Kiwi
from tokenize import tokenize, untokenize
from django.db.models import Count

kiwi = Kiwi(model_type="sbg")


class QuizGenerator:
    """무작위 퀴즈 만들기

    QuizGenerator([문제유형:list])

    문제 유형 순서

    1: 이지선다형

    2: 뜻풀이

    3: 빈칸 채우기

    4: 십자말 풀이
    """

    def __init__(self, puzzle: list):
        # 매개변수 체크
        if any(not isinstance(p, int) for p in puzzle):
            raise ValueError("문제 유형 개수 중에 int값이 아닌 게 포함되어 있습니다.")

        # 문제 유형[이지선다, 뜻풀이, 빈칸 채우기, 십자말 풀이 순]
        self.puzzle_category = {
            1: self.one_of_two,
            2: self.meaning,
            3: self.fill_in_the_blank,
            4: self.crossword_puzzle,
        }

        # 문제 개수
        self._counts = sum(puzzle)
        self._puzzles = puzzle

    # def generate(self):
    #     quiz_objects_ids = self.model.objects.values_list("id", flat=True)
    #     id_list = list(quiz_objects_ids)

    #     quiz_ids = random.sample(id_list, k=self._count)

    #     return self.model.objects.filter(id__in=quiz_ids)

    def generator(self):
        puzzle_list = dict()

        # 각 퍼즐 개수
        puzzle_list["counts"] = self._puzzles

        # 퍼즐 결과
        for i, c in enumerate(self._puzzles, start=1):
            if c != 0:
                puzzle_list[self.puzzle_category[i].__name__] = self.puzzle_category[i](
                    c
                )
        return puzzle_list

    def one_of_two(self, puzzle_count):
        quiz_objects_ids = NaverQuiz.objects.values_list("id", flat=True)
        id_list = list(quiz_objects_ids)
        quiz_ids = random.sample(id_list, k=puzzle_count)
        quiz = NaverQuiz.objects.filter(id__in=quiz_ids)
        serializer = NaverQuizSerializer(quiz, many=True)
        return serializer.data

    def meaning(self, puzzle_count):
        pass

    def fill_in_the_blank(self, puzzle_count):
        """빈칸에 알맞은 말 맞추기

        Args:
            puzzle_count (int): 배정된 퍼즐 수

        Returns:
            serializer.data : 시리얼라이즈된 데이터 리턴
        """

        # 최대 예문 개수
        _maximum_explain = 3

        # 전체 설명문 개수 count
        all_quiz_count = KrDictQuizExplain.objects.all().count()
        all_quiz_array = range(0, all_quiz_count + 1)
        quiz = []
        serializer = FillInTheBlankSerializer()

        # 뽑은 샘플 중에 적합하지 않은 쿼리셋이 있을 경우 다시 뽑음
        while len(quiz) < puzzle_count:
            random_num = random.sample(all_quiz_array, k=puzzle_count)

            # 샘플 중에 예문이 3개 미만인 경우 제외
            quiz = (
                KrDictQuizExplain.objects.filter(id__in=random_num)
                .annotate(all_examples_sum=Count("dict_word__examples"))
                .filter(all_examples_sum__gte=3)
            )

            serializer = FillInTheBlankSerializer(quiz, many=True)

        # kiwi 라이브러리 이용 단어 구멍 뚫기
        for k in range(puzzle_count):
            right_answer = serializer.data[k]["dict_word"]["word"]
            right_answer_tokenizes = kiwi.tokenize(right_answer)
            subtract_word = list()
            for rat in right_answer_tokenizes:
                if rat.tag != "EF":
                    subtract_word.append(rat)

            examples = serializer.data[k]["dict_word"]["examples"]
            emptyed_examples = list()
            for example in examples:
                tokenized_example = kiwi.tokenize(example["content"])
                for te in tokenized_example:
                    if te.form in [form.form for form in subtract_word]:
                        example["content"] = (
                            example["content"][: te.start]
                            + "O" * te.len
                            + example["content"][te.start + te.len :]
                        )

                emptyed_examples.append(example)

            # 구멍 뚫은 예제로 대체
            examples = emptyed_examples

            # 예제 개수 제한
            all_examples = serializer.data[k]["dict_word"]["examples"]
            examples_list = list()
            checked_list = list()
            count = 0
            _max_count = 100
            while len(examples_list) < _maximum_explain and count < _max_count + 1:
                ran_num = random.randint(0, len(all_examples) - 1)

                if ran_num not in checked_list:
                    checked_list.append(ran_num)

                picked_example = all_examples[ran_num]["content"]
                if picked_example not in examples_list and "O" in picked_example:
                    examples_list.append(picked_example)
                count += 1

            serializer.data[k]["dict_word"]["examples"] = examples_list

        return serializer.data

    def crossword_puzzle(self, puzzle_count):
        _array_size = 8  # 행렬 크기
        _voca_number = 5  # 단어 수

        voca_array = np.empty((_array_size, _array_size), dtype=list)

        #
        # print(voca_array)
