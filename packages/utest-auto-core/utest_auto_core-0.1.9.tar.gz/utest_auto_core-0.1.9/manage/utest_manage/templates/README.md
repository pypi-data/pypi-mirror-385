UTest 自动化测试框架 - 快速上手

本框架基于 ubox-py-sdk，提供简洁的测试用例编写与执行能力：步骤与断言、截图、录制、logcat 采集、性能采集与报告导出等。

## 1. 基础配置（config.yml）

关键项：
- task.serial_num：设备序列号
- task.os_type：android | ios | hm
- task.app_name：被测应用包名或安装包
- test.selected_tests：要执行的用例名称（为空执行全部）

## 2. 运行测试

- 更改配置文件后直接运行（读取 config.yml）：
```bash
uv run start_test.py
```

执行后输出目录：
- test_result/log/<用例名>/：用例日志（perf.json、logcat.txt 等）
- test_result/case/<用例名>/pic/：截图
- Excel 报告：在 test_result/log 根目录生成

## 3. 如何编写用例

参考：
- 真实业务：test_cases/user_tests_0.py（腾讯视频小游戏）
- Demo：test_cases/user_tests_1.py（框架能力演示）

示例骨架：
```python
from core.test_case import TestCase, StepStatus, FailureStrategy
from ubox_py_sdk import Device

class MyTest(TestCase):
    def __init__(self, device: Device):
        super().__init__(name="我的用例", description="用例描述", device=device)
        self.failure_strategy = FailureStrategy.STOP_ON_FAILURE

    def setup(self):
        # （可选）启动被测应用
        pkg = self.get_package_name()
        if pkg:
            self.start_step("启动应用", f"启动: {pkg}")
            ok = self.device.start_app(pkg)
            self.assert_true("应用应成功启动", ok)
            self.end_step(StepStatus.PASSED if ok else StepStatus.FAILED)
        # 录制（路径自动记录到结果）
        self.start_record()
        # logcat（仅记录文件路径，不需要手动停止）
        self.start_logcat()

    def run_test(self):
        # 步骤与断言
        self.start_step("准备场景", "示例")
        self.assert_true("环境应就绪", True)
        self.end_step(StepStatus.PASSED)

        # 关键阶段开启性能采集
        self.start_step("开启性能采集", "开始perf")
        started = self.start_perf()
        self.assert_true("性能采集应成功启动", started)
        self.end_step(StepStatus.PASSED if started else StepStatus.FAILED)

        # 业务操作...
        # ...
        # 停止性能采集：停止后自动解析 get_log_dir()/perf.json
        self.stop_perf()

    def teardown(self):
        # 停止录制
        self.stop_record()
        # （可选）关闭应用并回到桌面
        pkg = self.get_package_name()
        if pkg:
            self.device.stop_app(pkg)
        self.device.press("HOME")
```

要点与要求：
- 用例名称/描述：在 __init__ 的 name、description 设置。
- 步骤管理：start_step/end_step；在步骤内断言失败会自动标记结果，end_step 不是必须显式调用，但建议在成功路径显式结束以便报告更清晰。
- 断言：assert_true、assert_equal、assert_contains 等；失败按策略决定是否中断。
- 截图：失败/通过（可配置）时自动截图，也可随时 take_screenshot("name")。
- 录制：start_record()/stop_record()；只记录文件路径，报告展示。
- logcat：start_logcat()；记录输出文件路径（logcat.txt），报告展示。
- 性能：start_perf()/stop_perf()；设备端在停止时写入 get_log_dir()/perf.json，框架自动解析并汇总 FPS/Jank/CPU/GPU/温度/功耗/内存/网络等指标到报告。

## 4. 报告
- 自动生成 Excel 报告，包含：
  - 用例信息与状态
  - 步骤详情与截图
  - 录制与 logcat 文件路径
  - 性能监控关键指标（从 perf.json 解析的汇总）

## 5. 建议
- 步骤小而清晰、断言贴近业务、仅在关键路径采集性能、出错即截图便于复盘。


