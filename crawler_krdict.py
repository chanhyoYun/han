import json
import os
from dotenv import load_dotenv

# dotenv에서 key값을 참조하기 때문에 dotenv를 load 해와야 함
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from crawled_data.models import KrDictQuiz, KrDictQuizExample, KrDictQuizExplain

with open(
    "F:/nbc/final_project/전체 내려받기_한국어기초사전_JSON_20230612/1079331_51959.json",
    "r",
    encoding="utf-8",
) as file:
    data = json.load(file)

word_list = data["LexicalResource"]["Lexicon"]["LexicalEntry"]


def kr_dict():
    word_data = []

    for i in range(len(word_list)):
        # word 단어
        my_word = ""
        lemma = word_list[i]["Lemma"]
        if isinstance(lemma, list):
            for item in lemma:
                if item["feat"]["att"] == "writtenForm":
                    my_word = item["feat"]["val"]
        else:
            my_word = lemma["feat"]["val"]

        # explain과 example
        sense = word_list[i]["Sense"]
        if isinstance(sense, list):
            feats = [sense[j]["feat"] for j in range(len(sense))]
            sense_examples = []
            for k in range(len(sense)):
                try:
                    sense_examples.append(sense[k]["SenseExample"])
                except KeyError:
                    sense_examples.append(None)

        else:
            feats = sense["feat"]
            try:
                sense_examples = [sense["SenseExample"]]
            except KeyError:
                sense_examples = None

        my_explain = []
        if isinstance(feats, list):
            for feat in feats:
                if isinstance(feat, list):
                    for item in feat:
                        if item["att"] == "definition":
                            my_explain.append(item["val"])
                else:
                    my_explain.append(feat["val"])
        else:
            if feats["att"] == "definition":
                my_explain.append(feats["val"])

        # difficulty 난이도
        # 0(없음), 1(초급), 2(중급), 3(고급)
        my_difficulty = 0
        try:
            feat = word_list[i]["feat"]
            dif = {"없음": 0, "초급": 1, "중급": 2, "고급": 3}
            if isinstance(feat, list):
                for item in feat:
                    if item["att"] == "vocabularyLevel":
                        my_difficulty = dif[item["val"]]
            else:
                if feat.get("att") == "vocabularyLevel":
                    my_difficulty = dif[feat["val"]]
        except KeyError:
            pass

        # example 단어 예시 - type, contents
        my_all_examples = []
        if sense_examples is not None:
            for examples in sense_examples:
                if examples is not None:
                    if isinstance(examples, list):
                        for example in examples:
                            skip_example = False
                            for ex in example["feat"]:
                                # "대화"인 경우에는 현재의 example을 건너뜀
                                if ex["val"] == "대화":
                                    skip_example = True
                                    break
                                if ex["att"] == "type":
                                    my_type = ex["val"]
                                elif ex["att"] == "example":
                                    my_content = ex["val"]
                            if not skip_example:
                                my_all_examples.append({my_type: my_content})
                    else:
                        for ex in examples["feat"]:
                            if ex["att"] == "type":
                                my_type = ex["val"]
                            elif ex["att"] == "example":
                                my_content = ex["val"]
                        my_all_examples.append({my_type: my_content})

        complete_word = {
            "word": my_word,
            "explain": my_explain,
            "difficulty": my_difficulty,
            "example": my_all_examples,
        }

        word_data.append(complete_word)
    return word_data


if __name__ == "__main__":
    dict_words = kr_dict()
    for dict_word in dict_words:
        my_word = KrDictQuiz(word=dict_word["word"], difficulty=dict_word["difficulty"])
        my_word.save()
        for explain in dict_word["explain"]:
            my_explain = KrDictQuizExplain(dict_word=my_word, content=explain)
            my_explain.save()
        for example in dict_word["example"]:
            if "구" in example:
                my_type = 0
                my_content = example["구"]
            if "문장" in example:
                my_type = 1
                my_content = example["문장"]
            my_example = KrDictQuizExample(
                dict_word=my_word, word_type=my_type, content=my_content
            )
            my_example.save()
    print("데이터 베이스에 저장 완료!!")


# with open("words.json", "w", encoding="utf-8") as file:
#     json.dump(word_data, file, ensure_ascii=False)
