#!/usr/bin/env python3

import time
import traceback
import random
from core.test_case import TestCase, StepStatus, FailureStrategy
from ubox_py_sdk import DriverType, OSType, DeviceButton, EventHandler, Device


class TestCase1(TestCase):
    """框架使用示例用例（Demo）

    演示内容：
    1) 用例名称/描述设置（见 __init__）
    2) 步骤管理（start_step/end_step）end_step不是必须调用的，在断言中会自动设置结果
    3) 断言（assert_true/assert_equal 等）
    4) 录制（start_record/stop_record）
    5) logcat 采集（start_logcat）
    6) 性能采集（start_perf/stop_perf，停时自动解析 perf.json 并写入报告）
    """

    def __init__(self, device: Device):
        # 设置用例名称与描述（会显示在报告中）
        super().__init__(
            name="框架示例用例",
            description="演示步骤/断言/性能采集/logcat/录制等能力",
            device=device
        )
        # 初始化事件处理器（如需使用，可在用例内添加 watcher 等逻辑）
        self.event_handler = self.device.handler
        # 失败策略：失败是否继续执行。这里采用“遇错即停”，更贴近日常回归诉求
        # 如需收集全部失败可切换为 FailureStrategy.CONTINUE_ON_FAILURE
        self.failure_strategy = FailureStrategy.STOP_ON_FAILURE

    def setup(self) -> None:
        """测试前置操作
        - 仅做通用初始化类工作
        - 如需启动被测应用，可通过 get_package_name() 获取配置中的包名并启动
        """
        self.log_info("开始准备测试环境...")

        # 示例：如果配置了包名，则启动APP
        package_name = self.get_package_name()
        if package_name:
            self.start_step("启动应用", f"启动应用: {package_name}")
            success = self.device.start_app(package_name)
            self.assert_true("应用应成功启动", success)
            self.end_step(StepStatus.PASSED if success else StepStatus.FAILED)
        else:
            self.log_info("未配置应用包名，跳过应用启动")

        # 开始录制，录制文件路径会自动记录到测试结果中
        self.start_record()

        # 启动 logcat 采集（返回 LogcatTask，无需手动停止；只记录文件路径用于报告展示）
        self.start_logcat()

    def teardown(self) -> None:
        """测试后置操作
        - 手动停止录制
        - 可选择性地关闭应用、回到桌面
        """
        self.log_info("开始清理测试环境...")

        # 停止录制（录制停止后会在报告中展示录屏文件路径）
        self.stop_record()

        # 如果需要，可在此处停止被测应用并回到主界面
        package_name = self.get_package_name()
        if package_name:
            self.device.stop_app(package_name)
            self.log_info(f"应用已停止: {package_name}")
        self.device.press(DeviceButton.HOME)
        self.log_info("已返回主界面")

    def run_test(self) -> None:
        """执行示例测试
        - 演示步骤编排与断言
        - 演示关键阶段开启性能监控
        """
        # 步骤1：进入页面/准备场景（示例）
        self.start_step("准备场景", "示例：准备业务前置条件")
        time.sleep(1)
        # 示例断言：总是为真（真实项目中请替换为业务校验）
        self.assert_true("示例断言：环境已就绪", True)
        self.end_step(StepStatus.PASSED)

        # 步骤2：关键路径 - 开启性能监控
        self.start_step("开启性能监控", "在关键路径前启动性能采集")
        perf_started = self.start_perf()
        self.assert_true("性能采集应成功启动", perf_started)
        self.end_step(StepStatus.PASSED if perf_started else StepStatus.FAILED)

        try:
            # 步骤3：执行核心业务操作（示例）
            self.start_step("核心操作", "执行示例性业务流程")
            time.sleep(2)  # 这里模拟业务耗时
            # 示例的等值断言（真实项目中替换为实际校验）
            self.assert_equal("示例断言：结果应相等", actual=1 + 1, expected=2)
            self.end_step(StepStatus.PASSED)

            # 步骤4：收尾校验
            self.start_step("收尾校验", "示例：检查数据/页面状态")
            time.sleep(1)
            self.assert_true("示例断言：收尾检查通过", True)
            self.end_step(StepStatus.PASSED)
        finally:
            # 性能监控需要显式停止，停止后会自动解析 get_log_dir()/perf.json 并入报告
            self.stop_perf()