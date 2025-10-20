# -*- coding: utf-8 -*-

from pydantic import BaseModel, Field
from ..typehint import T_NUM
from ..logger import logger


class AddUpTwoNumberInput(BaseModel):
    v1: T_NUM = Field(description="The first number to add.")
    v2: T_NUM = Field(description="The second number to add.")

    def main(self):
        logger.info(f"v1 = {self.v1}")  # for debug only
        logger.info(f"v2 = {self.v2}")  # for debug only
        result = self.v1 + self.v2
        logger.info(f"{result = }")  # for debug only
        return AddUpTwoNumberOutput(
            input=self,
            result=result,
        )


class AddUpTwoNumberOutput(BaseModel):
    input: AddUpTwoNumberInput = Field()
    result: T_NUM = Field(description="The result of adding the two numbers.")
