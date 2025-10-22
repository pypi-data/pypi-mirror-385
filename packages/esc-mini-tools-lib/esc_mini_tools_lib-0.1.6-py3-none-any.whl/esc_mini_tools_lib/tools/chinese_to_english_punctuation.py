# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field
from pathlib import Path

dir_here = Path(__file__).absolute().parent
p_input = dir_here / "input.txt"
p_output = dir_here / "output.txt"

chinese_punctuation = "，、。；：？！“”‘’（）【】《》"


def _process_last_special_char(line: str, tokens: list[str], char: str):
    try:
        if line.rstrip()[-1] == char:
            tokens.append("")
    except IndexError:
        pass


def handle_dou_hao(line: str) -> str:
    """
    中文逗号 ， → 英文逗号 ,
    并在逗号后添加一个空格
    """
    tokens = [token.strip() for token in line.split("，") if token.strip()]
    _process_last_special_char(line, tokens, "，")
    return ", ".join(tokens).strip()


def handle_dun_hao(line: str) -> str:
    """
    中文顿号 、 → 英文逗号 ,
    并在逗号后添加一个空格
    """
    tokens = [token.strip() for token in line.split("、") if token.strip()]
    _process_last_special_char(line, tokens, "、")
    return ", ".join(tokens).strip()


def handle_ju_hao(line: str) -> str:
    """
    中文句号 。 → 英文句号 .
    并在句号后添加一个空格
    """
    tokens = [token.strip() for token in line.split("。") if token.strip()]
    _process_last_special_char(line, tokens, "。")
    return ". ".join(tokens).strip()


def handle_mao_hao(line: str) -> str:
    """
    中文冒号 ： → 英文冒号 :
    并在冒号后添加一个空格
    """
    tokens = [token.strip() for token in line.split("：") if token.strip()]
    _process_last_special_char(line, tokens, "：")
    return ": ".join(tokens).strip()


def handle_fen_hao(line: str) -> str:
    """
    中文分号 ； → 英文分号 ;
    并在分号后添加一个空格
    """
    tokens = [token.strip() for token in line.split("；") if token.strip()]
    _process_last_special_char(line, tokens, "；")
    return "; ".join(tokens).strip()


def handle_wen_hao(line: str) -> str:
    """
    中文问号 ？ → 英文问号 ?
    并在问号后添加一个空格
    """
    tokens = [token.strip() for token in line.split("？") if token.strip()]
    _process_last_special_char(line, tokens, "？")
    return "? ".join(tokens).strip()


def handle_exclamation(line: str) -> str:
    """
    中文感叹号 ！ → 英文感叹号 !
    并在感叹号后添加一个空格
    """
    tokens = [token.strip() for token in line.split("！") if token.strip()]
    _process_last_special_char(line, tokens, "！")
    return "! ".join(tokens).strip()


def handle_zuo_kuo_hao(line: str) -> str:
    """
    中文左括号 （ → 英文左括号 (
    并在左括号前添加一个空格
    """
    tokens = [token.strip() for token in line.split("（") if token.strip()]
    return " (".join(tokens).strip()


def handle_you_kuo_hao(line: str) -> str:
    """
    中文右括号 ） → 英文右括号 )
    并在右括号后添加一个空格. 但如果右括号之后是一个特殊标点符号, 则不添加空格.
    """
    tokens = [token.strip() for token in line.split("）") if token.strip()]
    # print(tokens)  # for debug only
    new_tokens = list()
    for ith, token in enumerate(tokens):
        new_tokens.append(token)
        try:
            next_token = tokens[ith + 1]
            if next_token[0] in ",.:;?!":
                new_tokens.append(")")
            else:
                new_tokens.append(") ")
        except IndexError:
            break
    try:
        if line.rstrip()[-1] == "）":
            new_tokens.append(")")
    except IndexError:
        pass
    # print(new_tokens)  # for debug only
    return "".join(new_tokens).strip()


def handle_zuo_shuang_yin_hao(line: str) -> str:
    """
    中文左双引号 “ → 英文左双引号 "
    并在左双引号前添加一个空格
    """
    tokens = [token.strip() for token in line.split("“") if token.strip()]
    return ' "'.join(tokens).strip()


def handle_you_shuang_yin_hao(line: str) -> str:
    """
    中文右双引号 ” → 英文右双引号 "
    并在右双引号后添加一个空格. 但如果右双号之后是一个特殊标点符号, 则不添加空格.
    """
    tokens = [token.strip() for token in line.split("”") if token.strip()]
    # print(tokens)  # for debug only
    new_tokens = list()
    for ith, token in enumerate(tokens):
        new_tokens.append(token)
        try:
            next_token = tokens[ith + 1]
            if next_token[0] in ",.:;?!)":
                new_tokens.append('"')
            else:
                new_tokens.append('" ')
        except IndexError:
            break
    try:
        if line.rstrip()[-1] == "”":
            new_tokens.append('"')
    except IndexError:
        pass
    # print(new_tokens)  # for debug only
    return "".join(new_tokens).strip()


def handle_space_between_chinese_and_english(line: str) -> str:
    """
    Add space between Chinese and English characters/numbers.
    Goes through character by character and maintains two consecutive characters.
    If one is an English letter/number (a-z, A-Z, 0-9) and the other is non-ASCII, add space between them.
    Also adds space between English letters and numbers.
    """
    if not line:
        return line

    result = []
    prev_char = None

    for current_char in line:
        # Check if we need to add space between prev_char and current_char
        if prev_char is not None:
            # Check character types
            prev_is_english = prev_char.isalpha() and ord(prev_char) < 128
            current_is_english = current_char.isalpha() and ord(current_char) < 128
            prev_is_number = prev_char.isdigit()
            current_is_number = current_char.isdigit()
            prev_is_non_ascii = ord(prev_char) >= 128
            current_is_non_ascii = ord(current_char) >= 128

            # Add space in the following cases:
            if (
                # 1. Between English letter and non-ASCII character, example: "Eng中文"
                (prev_is_english and current_is_non_ascii)
                # 2. Between non-ASCII character and English letter, example: "中文Eng"
                or (prev_is_non_ascii and current_is_english)
                # 3. Between number and non-ASCII character, example: "100中文"
                or (prev_is_number and current_is_non_ascii)
                # 4. Between non-ASCII character and number, example: "中文100"
                or (prev_is_non_ascii and current_is_number)
            ):
                result.append(" ")

        result.append(current_char)
        prev_char = current_char

    return "".join(result)


def handle_everything(line: str) -> str:
    line = handle_dou_hao(line)
    line = handle_dun_hao(line)
    line = handle_ju_hao(line)
    line = handle_mao_hao(line)
    line = handle_fen_hao(line)
    line = handle_wen_hao(line)
    line = handle_exclamation(line)
    line = handle_zuo_kuo_hao(line)
    line = handle_you_kuo_hao(line)
    line = handle_zuo_shuang_yin_hao(line)
    line = handle_you_shuang_yin_hao(line)
    # Add spaces between Chinese and English after all punctuation conversions
    line = handle_space_between_chinese_and_english(line)
    return line


def process(text: str) -> str:
    lines = text.splitlines()
    new_lines = [handle_everything(line) for line in lines]
    return "\n".join(new_lines)


class ChineseToEnglishPunctuationInput(BaseModel):  # pragma: no cover
    text: str = Field()

    def main(self):
        result = process(self.text)
        return ChineseToEnglishPunctuationOutput(
            input=self,
            result=result,
        )


class ChineseToEnglishPunctuationOutput(BaseModel):  # pragma: no cover
    input: ChineseToEnglishPunctuationInput = Field()
    result: str = Field()
