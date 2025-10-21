
import json

from pro_craft.log import Log
logger = Log.logger
editing_log = logger.debug





############evals##############

 # 异步
class Base_Evals():
    def __init__(self):
        """
        # TODO 2 自动优化prompt 并提升稳定性, 并测试
        通过重写继承来使用它
        """
        self.MIN_SUCCESS_RATE = 00.0 # 这里定义通过阈值, 高于该比例则通过


    async def _assert_eval_function(self,params):
        #这里定义函数的评价体系
        print(params,'params')

    async def get_success_rate(self,test_cases:list[tuple]):
        """
                # 这里定义数据

        """

        successful_assertions = 0
        total_assertions = len(test_cases)
        result_cases = []

        for i, params in enumerate(test_cases):
            try:
                # 这里将参数传入
                await self._assert_eval_function(params)
                successful_assertions += 1
                result_cases.append({"type":"Successful","--input--":params,"evaluate_info":f"满足要求"})
            except AssertionError as e:
                result_cases.append({"type":"FAILED","--input--":params,"evaluate_info":f"ERROR {e}"})
            except Exception as e: # 捕获其他可能的错误
                result_cases.append({"type":"FAILED","--input--":params,"evaluate_info":f"ERROR {e}"})


        success_rate = (successful_assertions / total_assertions) * 100
        print(f"\n--- Aggregated Results ---")
        print(f"Total test cases: {total_assertions}")
        print(f"Successful cases: {successful_assertions}")
        print(f"Success Rate: {success_rate:.2f}%")

        if success_rate >= self.MIN_SUCCESS_RATE:
            return "通过", json.dumps(result_cases,ensure_ascii=False)
        else:
            return "未通过",json.dumps(result_cases,ensure_ascii=False)


    def global_evals():
        pass





