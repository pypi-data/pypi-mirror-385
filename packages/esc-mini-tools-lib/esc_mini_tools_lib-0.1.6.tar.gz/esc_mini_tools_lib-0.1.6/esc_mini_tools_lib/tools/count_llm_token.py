# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field
import tiktoken
from ..logger import logger


class CountLlmTokenInput(BaseModel):
    text: str = Field(description="The text to count tokens for.")

    def main(self):
        logger.info(f"text = {self.text!r}")  # for debug only
        enc = tiktoken.encoding_for_model("gpt-4o")
        tokens = enc.encode(self.text)
        result = len(tokens)
        logger.info(f"{result = }")  # for debug only
        return CountLlmTokenOutput(
            input=self,
            result=result,
        )


class CountLlmTokenOutput(BaseModel):
    input: CountLlmTokenInput = Field()
    result: int = Field(description="The number of tokens in the text.")