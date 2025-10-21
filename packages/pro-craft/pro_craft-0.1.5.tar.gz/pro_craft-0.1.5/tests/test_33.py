from pydantic import BaseModel, Field, model_validator, field_validator

from pro_craft.prompt_helper import Intel, IntellectType

intels = Intel()



task_1 = "素材提取-从文本中提取素材"

class Varit(BaseModel):
    material : str
    protagonist: str

task_2 = "素材提取-验证素材的正确性"

class Varit2(BaseModel):
    material : str
    real : str

def work():

    result0 = "你好"

    result1 = intels.intellect_remove_format(input_data = result0,
                                            OutputFormat = Varit,
                                            prompt_id = task_1,
                                            version = None,
                                            inference_save_case = True)

    result2 = intels.intellect_remove_format(input_data = result1,
                                            OutputFormat = Varit2,
                                            prompt_id = task_2,
                                            version = None,
                                            inference_save_case = True)

    print(result2)

work()
