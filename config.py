from pathlib import Path

with (
    open(file=Path('static/stopwords_in_russian.txt'), encoding='utf-8') as file_rus,
    open(file=Path('static/stopwords_in_english.txt'), encoding='utf-8') as file_eng
):
    STOP_WORDS_RUS = set(file_rus.read().split())
    STOP_WORDS_ENG = set(file_eng.read().split())

data_storage = {}
NUMBER_OF_LINES = 50
