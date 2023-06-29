from crawled_data.models import NaverQuiz, KrDictQuiz, KrDictQuizExplain
from crawled_data.serializers import (
    NaverQuizSerializer,
    FillInTheBlankSerializer,
    MeaningSerializer,
)
import random
import numpy as np
from kiwipiepy import Kiwi
from django.db.models import Count
from django.db.models import Prefetch
from django.contrib.postgres.aggregates import ArrayAgg
from jamo import h2j, j2hcj

kiwi = Kiwi(model_type="sbg")
import json


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
        """초기 설정

        Args:
            puzzle (list): 문제유형

        Raises:
            TypeError: 문제 유형에 int값 아닌 경우 에러 발생
        """
        self._all_quiz_count = KrDictQuiz.objects.all().count()
        # 매개변수 체크
        if any(not isinstance(p, int) for p in puzzle):
            raise TypeError("문제 유형 개수 중에 int값이 아닌 게 포함되어 있습니다.")

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

    def generator(self):
        """전체 문제 생성기

        Returns:
            puzzle_list(dict): 각 함수에서 문제 유형 개수만큼 문제들 리턴받아 딕셔너리로 저장해서 리턴
        """

        puzzle_list = {}

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
        """이지선다형 생성

        Args:
            puzzle_count (int): 이지선다형 문제 개수

        Returns:
            _type_: _description_
        """
        quiz_objects_ids = NaverQuiz.objects.values_list("id", flat=True)
        id_list = list(quiz_objects_ids)
        quiz_ids = random.sample(id_list, k=puzzle_count)
        quiz = NaverQuiz.objects.filter(id__in=quiz_ids)
        serializer = NaverQuizSerializer(quiz, many=True)
        return serializer.data

    def meaning(self, puzzle_count):
        """단어의 의미를 주고 몇 번이 답인지 맞추기 생서


        Args:
            puzzle_count (int): 배정된 퍼즐 수
        """

        # 전체 설명문 개수 count
        all_quiz_array = range(0, self._all_quiz_count + 1)
        random_num = random.sample(all_quiz_array, k=puzzle_count)
        right_answer_quiz = KrDictQuiz.objects.filter(id__in=random_num)

        serializer = MeaningSerializer(right_answer_quiz, many=True)

        return serializer.data

    def fill_in_the_blank(self, puzzle_count):
        """빈칸에 알맞은 말 맞추기 생성

        Args:
            puzzle_count (int): 배정된 퍼즐 수

        Returns:
            serializer.data : 시리얼라이즈된 데이터 리턴
        """

        # 최대 예문 개수
        _maximum_explain = 3

        # 전체 설명문 개수 count
        all_quiz_array = range(0, self._all_quiz_count + 1)
        quiz = []
        # 빈 시리얼라이즈 만들기
        serializer = FillInTheBlankSerializer()

        # 뽑은 샘플 중에 적합하지 않은 쿼리셋이 있을 경우 다시 뽑음
        while len(quiz) < puzzle_count:
            random_num = random.sample(all_quiz_array, k=puzzle_count)

            # 샘플 중에 예문이 최대 예문 개수 미만인 경우 제외
            quiz = (
                KrDictQuizExplain.objects.filter(id__in=random_num)
                .annotate(all_examples_sum=Count("dict_word__examples"))
                .filter(all_examples_sum__gte=_maximum_explain)
            )

            serializer = FillInTheBlankSerializer(quiz, many=True)

        # kiwi 라이브러리 이용 단어 구멍 뚫기
        for k in range(puzzle_count):
            right_answer = serializer.data[k]["dict_word"]["word"]
            # 자음 힌트
            allInit = []
            for x in serializer.data[k]["dict_word"]["word"]:
                temp = h2j(x)
                imf = j2hcj(temp)  # init,middle,final
                allInit.append(imf[0])

            voca_hint = "".join(allInit)
            serializer.data[k]["dict_word"]["hint"] = voca_hint

            # 정답 토크나이징
            right_answer_tokenizes = kiwi.tokenize(right_answer)
            subtract_word = []
            # 토크나이징한 정답 중에서 어미 제외하고 subtract_word로 다시 합치기
            for rat in right_answer_tokenizes:
                # 어미 제외
                if rat.tag != "EF":
                    subtract_word.append(rat)

            examples = serializer.data[k]["dict_word"]["examples"]
            emptyed_examples = []
            # 각 예제들 토크나이징
            for example in examples:
                tokenized_example = kiwi.tokenize(example["content"])
                # 토크나이징한 예제 형태소 들 중에서 토크나이징한 정답에 포함되는 형태소들 O로 대체
                for te in tokenized_example:
                    if te.form in [form.form for form in subtract_word]:
                        example["content"] = (
                            example["content"][: te.start]
                            + "O" * te.len
                            + example["content"][te.start + te.len :]
                        )

                emptyed_examples.append(example)

            # 예제를 O으로 구멍 뚫은 예제로 대체
            examples = emptyed_examples

            # 예제 개수 제한
            all_examples = serializer.data[k]["dict_word"]["examples"]
            examples_list = []
            checked_list = []
            count = 0
            _max_count = 100
            # 성능 문제로 최대 100번으로 제한
            while len(examples_list) < _maximum_explain and count < _max_count + 1:
                ran_num = random.randint(0, len(all_examples) - 1)

                # 랜덤으로 픽한 예제 중복되지 않도록 제한
                if ran_num not in checked_list:
                    checked_list.append(ran_num)

                picked_example = all_examples[ran_num]["content"]
                # 랜덤으로 선택한 예제 중에 아직 examples_list에 포함되어 있지 않고 O을 포함하고 있는 예제를 추가
                if picked_example not in examples_list and "O" in picked_example:
                    examples_list.append(picked_example)
                count += 1

            # 시리얼라이징한 데이터 중에 선택된 examples_list리스트로 대체
            serializer.data[k]["dict_word"]["examples"] = examples_list

        return serializer.data

    def crossword_puzzle(self, puzzle_count):
        """십자말퍼즐 생성

        Args:
            puzzle_count (int): 십자말퍼즐 개수

        Raises:
            ValueError: 문제 뽑아내는 시간 고려 0 혹은 1개로 제한

        Returns:
            json_cross_word(dict): json화한 십자말퍼즐 데이터
        """
        # 문제 뽑아내는 시간이 너무 길어서 1개로 제한
        if puzzle_count > 1:
            raise ValueError("십자말퍼즐은 0 혹은 1개만 가능합니다.")

        # 고정 변수. 필요시 수정 가능
        _array_size = 6  # 행렬 크기
        _voca_number = 8  # 단어 수

        # CrossWordPuzzleGenerator를 이용해 퍼즐 생성
        cross_word_puzzle = CrossWordPuzzleGenerator(_array_size, _voca_number)
        voca_array, voca_list = cross_word_puzzle.generate()
        json_cross_word = json.dumps(
            {"problems": voca_array, "problem_data": voca_list},
            ensure_ascii=False,
        )
        return json_cross_word


class CrossWordPuzzleGenerator:
    def __init__(self, size: int, num: int):
        self._all_quiz_count = KrDictQuiz.objects.all().count()  # 모든 단어 수 카운트
        self._array_size = size  # 행렬 크기
        self._voca_number = num  # 단어 수

        # 단어 설명들 중에서 content만 뽑아낸 prefetch
        explains_prefetch = Prefetch(
            "explains",
            queryset=KrDictQuizExplain.objects.only("content").exclude(
                content__contains="1"
            )[:2],
        )

        # 전체 단어 리스트
        self._word_list = (
            KrDictQuiz.objects.prefetch_related(explains_prefetch)
            .annotate(explains_content=ArrayAgg("explains__content"))
            .values_list("id", "word", "explains_content")
        )

        # 이미 사용된 단어의 인덱스 저장 (성능 개선)
        self.used_word_index = []

        # 방향 지정
        self._orientation = ["right", "bottom"]

        # 단어 집어넣는 거 실패 여부 체크하는 변수
        self.double = False

    def generate(self):
        """십자말 퍼즐 초기화 및 생성

        Returns:
            voca_array(list): 십자말퍼즐을 리스트형태로 변환해 리턴

            voca_list(dict): 십자말퍼즐 관련된 데이터들 저장해 리턴
        """
        # 십자말 퍼즐 초기화
        voca_array = np.full((self._array_size, self._array_size), " ")

        # 단어 설명 목록
        voca_list = []

        # 최대 단어 개수만큼 뽑아낼 때까지 단어 삽입 시도
        while True:
            if self.voca_to_puzzle(voca_array, voca_list):
                if len(voca_list) >= self._voca_number:
                    break

        # 넘파이 배열을 리스트로 변환
        voca_array = voca_array.tolist()
        return voca_array, voca_list

    def voca_to_puzzle(self, puzzle, voca_list):
        """단어 추가하기"""

        # 지정한 단어 개수 넘으면 중지하고 리턴
        if len(voca_list) >= self._voca_number:
            return False
        else:
            # 첫 단어일 경우
            if len(voca_list) == 0:
                # 단어가 공백을 포함하거나 글자 길이 1일 경우 제외한 모든 단어 리스트
                voca_candidates = [
                    word
                    for i, word in enumerate(self._word_list)
                    if i not in self.used_word_index
                    and " " not in word[1]
                    and len(word[1]) > 1
                ]
                # 방향 랜덤
                orientation = random.choice(self._orientation)
                # 위치 좌상단 랜덤 (무작위 투입 시 실패할 때마다 새로 뽑아야 하므로 성능 고려해 아예 좌상단 고정)
                [row, col] = [
                    random.randint(0, self._array_size // 2 - 1),
                    random.randint(0, self._array_size // 2 - 1),
                ]

            # 두번째 단어부터
            else:
                if self.double:
                    # 실패하고 재시도할 경우 마지막 단어가 아니라 다른 단어에서 픽하기
                    last_word = random.choice(voca_list[:-1])["word"]
                else:
                    # 마지막으로 삽입한 단어 찾기
                    last_word = voca_list[-1]["word"]

                # 가능한 부분에 계속해서 삽입 시도
                while True:
                    # 마지막으로 삽입한 단어의 글자 중에서 하나 픽하기
                    pick_one_letter = random.choice(last_word)

                    # 동사, 형용사가 대부분 다로 끝나므로 픽한 글자가 '다'일 경우 제외
                    while True:
                        if pick_one_letter == "다":
                            pick_one_letter = random.choice(last_word)
                        elif self.find_words_starting_with(pick_one_letter) is False:
                            pick_one_letter = random.choice(last_word)
                        else:
                            break

                    # 기존에 배치된 단어의 랜덤한 글자로 시작하는 새로운 단어 리스트 중에서
                    # 단어가 공백을 포함하거나 글자 길이 1일 경우 제외한 모든 단어 리스트
                    voca_candidates = [
                        word
                        for word in self.find_words_starting_with(pick_one_letter)
                        if word[0] not in self.used_word_index
                        and " " not in word[1]
                        and len(word[1]) > 1
                    ]

                    # 방향, 위치 정하기
                    if self.double:
                        # 한번 실패했을 경우 방향, 위치 랜덤
                        positions = [
                            (row, col)
                            for row in range(self._array_size)
                            for col in range(self._array_size)
                        ]
                        random.shuffle(positions)
                        [row, col] = random.choice(positions)
                        orientation = random.choice(self._orientation)

                        break
                    else:
                        # 재시도가 아닐 경우 이전 글자에 따라서 방향을 바꾸고 픽한 글자의 위치를 전체 배열에서 지정해주기

                        if voca_list[-1]["orientation"] == "right":
                            orientation = "bottom"
                            [row, col] = [
                                voca_list[-1]["position"][0],
                                voca_list[-1]["position"][1]
                                + voca_list[-1]["word"].index(pick_one_letter),
                            ]
                        else:
                            orientation = "right"
                            [row, col] = [
                                voca_list[-1]["position"][0]
                                + voca_list[-1]["word"].index(pick_one_letter),
                                voca_list[-1]["position"][1],
                            ]

                        break

            # 선택된 단어 후보군들을 섞기
            random.shuffle(voca_candidates)

            # 섞은 후보군을 차례대로 선택해 넣어보기
            for word_info in voca_candidates:
                if self.try_place_word(
                    puzzle, voca_list, word_info, orientation, row, col
                ):
                    self.double = False
                    return True

            # 죄다 실패했을 때 self.double을 True로 바꾸고 다시 함수 실행
            self.double = True
            return False

    def find_words_starting_with(self, letter):
        """어떤 글자로 시작하는 단어 리스트 뽑기

        Args:
            letter (str): 선택된 글자

        Returns:
            matched_words(list): 선택된 글자로 시작하는 모든 단어 리스트
        """
        # KrDictQuiz에서 letter로 시작하는 단어들을 모두 찾아서 반환
        explains_prefetch = Prefetch(
            "explains",
            queryset=KrDictQuizExplain.objects.only("content").exclude(
                content__contains="1"
            )[:2],
        )

        # letter로 시작하는 단어를 뽑기
        matched_words = (
            KrDictQuiz.objects.filter(word__startswith=letter)
            .prefetch_related(explains_prefetch)
            .annotate(explains_content=ArrayAgg("explains__content"))
            .values_list("id", "word", "explains_content")
        )

        if len(matched_words) == 0:
            return False
        return matched_words

    def try_place_word(self, puzzle, voca_list, word_info, orientation, row, col):
        """삽입 가능한지 확인하고 넣는 함수"""

        # 김치, 김치볶음밥처럼 이미 voca_list에 서로간 포함되는 단어가 있을 경우 False 반환
        for info in voca_list:
            if word_info[1] in info["word"] or info["word"] in word_info[1]:
                return False
        # can_place_word함수에서 해당 위치, 해당 방향으로 단어가 들어갈 수 있는지 판단하고
        # True라면 place_word함수로 위치
        if self.can_place_word(puzzle, word_info[1], row, col, orientation):
            self.place_word(puzzle, word_info[1], row, col, orientation)

            # 자모 라이브러리로 단어의 초성만을 뽑아서 voca_hint로 반환
            allInit = []
            for x in word_info[1]:
                temp = h2j(x)
                imf = j2hcj(temp)  # init,middle,final
                allInit.append(imf[0])

            voca_hint = "".join(allInit)
            voca_info = {
                "word_num": word_info[0],
                "word": word_info[1],
                "explain": word_info[2],
                "hint": voca_hint,
                "position": (row, col),
                "orientation": orientation,
            }

            # voca_list에 삽입된 단어에 관련된 info들을 새로 삽입
            voca_list.append(voca_info)
            self.used_word_index.append(word_info[0])
            return True

        return False

    def can_place_word(self, puzzle, word, row, col, orientation):
        """삽입 가능 여부 판단 함수"""
        # 각 방향에 따라 단어가 추가됐을 때 이미 다른 단어가 위치해 있거나, 배열을 넘어가면 False리턴
        if orientation == "right":
            if col + len(word) > self._array_size:
                return False
            for i, letter in enumerate(word):
                # 만약 겹치는 위치의 문자가 현재 단어의 문자와 같지 않거나 빈 문자가 아니라면 False 반환
                if puzzle[row][col + i] != " " and puzzle[row][col + i] != letter:
                    return False
        elif orientation == "bottom":
            if row + len(word) > self._array_size:
                return False
            for i, letter in enumerate(word):
                # 만약 겹치는 위치의 문자가 현재 단어의 문자와 같지 않거나 빈 문자가 아니라면 False 반환
                if puzzle[row + i][col] != " " and puzzle[row + i][col] != letter:
                    return False
        return True

    def place_word(self, puzzle, word, row, col, orientation):
        """퍼즐에 단어 집어넣기

        Args:
            puzzle (numpy array): 퍼즐 배열
            word (str): 넣을 단어
            row (int): 세로 위치
            col (int): 가로 위치
            orientation (str): 방향
        """
        if orientation == "right":
            for i, letter in enumerate(word):
                puzzle[row][col + i] = letter
        elif orientation == "bottom":
            for i, letter in enumerate(word):
                puzzle[row + i][col] = letter
