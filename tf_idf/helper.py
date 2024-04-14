import math
import re
from collections import Counter, defaultdict
from io import BytesIO

import docx
from fastapi import UploadFile, File, HTTPException

from config import STOP_WORDS_RUS, STOP_WORDS_ENG, NUMBER_OF_LINES, data_storage

ALLOWED_TEXT_FILE_FORMATS = ['txt', 'csv', 'json', 'xml', 'html']


async def get_text_from_file(file: UploadFile = File(...)) -> str:
    file_path = file.filename.split('.')[-1]
    if file_path == "docx":
        file_bytes = await file.read()
        buffer = BytesIO(file_bytes)
        doc = docx.Document(buffer)
        return "".join(paragraph.text + "\n" for paragraph in doc.paragraphs).lower()
    elif file_path in ALLOWED_TEXT_FILE_FORMATS:
        return (await file.read()).decode("utf-8").lower()
    else:
        raise HTTPException(status_code=400, detail=f"Недопустимый формат файла {file_path}")


async def reformation_text(text: str) -> list[str]:
    from pymorphy3 import MorphAnalyzer
    morph = MorphAnalyzer()
    pattern = r"[^a-zA-Zа-яА-я0-9\s]"
    new_text = re.sub(pattern, '', text).replace("\n", " ").replace("\t", " ").replace("\b", " ").split()
    lemmatized_words = [morph.parse(word)[0].normal_form for word in new_text]
    text_without_stopwords = [word for word in lemmatized_words
                              if word not in STOP_WORDS_RUS and word not in STOP_WORDS_ENG]
    result = text_without_stopwords
    return result


async def count_tf(list_of_words: list[str]) -> dict:
    word_counts = Counter(list_of_words)
    total_words = len(list_of_words)
    tf = {
        word: word_counts[word] / total_words for word in word_counts
    }
    return tf


async def get_formatted_files(files: list[UploadFile]) -> list[list[str]]:
    return [await reformation_text(await get_text_from_file(file)) for file in files]


async def count_idf(formatted_files: list[list[str]]) -> dict:
    word_document_count = defaultdict(int)
    for doc in formatted_files:
        unique_words = set(doc)
        for word in unique_words:
            word_document_count[word] += 1

    total_documents = len(formatted_files)
    idf = {
        word: math.log(total_documents / count) for word, count in word_document_count.items()
    }

    return idf


async def get_result_table_word_tf_idf(files: list[UploadFile], number_of_lines: int = NUMBER_OF_LINES):
    list_of_words_in_all_files = await get_formatted_files(files)
    list_tf = [await count_tf(file) for file in list_of_words_in_all_files]
    idf = await count_idf(list_of_words_in_all_files)
    result = []
    for tf_dict in list_tf:
        combined_dict = {}
        for word, tf_value in tf_dict.items():
            idf_value = idf.get(word, 0.0)
            combined_dict[word] = [tf_value, idf_value]
        sorted_combined_dict = {k: v for k, v in
                                sorted(combined_dict.items(), key=lambda item: item[1][1], reverse=True)}

        result.append(sorted_combined_dict)
    if len(result) <= NUMBER_OF_LINES:
        return result
    else:
        return result[:NUMBER_OF_LINES]


async def save_data_in_storage(files: list[UploadFile] = File(...)):
    real_files = [file for file in files if file.size != 0]
    if not real_files:
        raise HTTPException(status_code=400, detail="Загрузите хотя бы один файл")
    data = await get_result_table_word_tf_idf(real_files)
    data_storage.clear()
    data_storage["data_for_tf_idf_tables"] = data
