"""
配置管理模块

提供全局配置管理功能，支持从配置文件加载参数
"""

import os
import json
import traceback

import yaml
from typing import Dict, Any, Optional, Union
from ubox_py_sdk import OSType, RunMode
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class DeviceConfig:
    """设备配置"""
    udid: str = None
    os_type: OSType = None
    auth_code: Optional[str] = None


@dataclass
class TaskConfig:
    """任务配置"""
    job_id: str = ""
    serial_num: str = ""
    os_type: str = "android"
    app_name: str = ""
    auth_code: Optional[str] = None


@dataclass
class UBoxConfig:
    """UBox配置"""
    secret_id: str
    secret_key: str
    mode: Union[str, RunMode] = RunMode.NORMAL


@dataclass
class TestConfig:
    """测试配置"""
    test_name: str
    test_description: str = ""
    screenshot_on_failure: bool = True  # 失败时截图
    screenshot_on_success: bool = False  # 成功时截图
    selected_tests: list = None  # 指定要运行的测试用例名称列表


@dataclass
class ReportConfig:
    """报告配置"""
    report_format: str = "excel"  # excel, json, html, all
    output_dir: str = "./test_result/log"  # 报告输出目录
    chart_quality: str = "high"  # 图表质量: low, medium, high
    theme: str = "default"  # 报告主题: default, dark, light


@dataclass
class FrameworkConfig:
    """框架全局配置"""
    ubox: UBoxConfig
    device: DeviceConfig
    test: TestConfig
    task: TaskConfig = field(default_factory=TaskConfig)
    report: ReportConfig = field(default_factory=ReportConfig)
    # 日志配置
    log_level: str = "INFO"


class ConfigManager:
    """配置管理器"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径，支持json和yaml格式
        """
        self.config_path = config_path
        self._config: Optional[FrameworkConfig] = None

    def load_config(self, config_path: Optional[str] = None) -> FrameworkConfig:
        """
        加载配置文件
        
        Args:
            config_path: 配置文件路径，如果为None则使用初始化时的路径
            
        Returns:
            FrameworkConfig: 加载的配置对象
        """
        if config_path:
            self.config_path = config_path

        if not self.config_path or not os.path.exists(self.config_path):
            # 使用默认配置
            raise ValueError("配置文件未找到")

        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                if self.config_path.endswith('.yaml') or self.config_path.endswith('.yml'):
                    config_data = yaml.safe_load(f)
                else:
                    config_data = json.load(f)

            return self._parse_config(config_data)

        except Exception as e:
            raise ValueError(f"配置文件加载失败: {e}\n{traceback.format_exc()}")

    def _parse_config(self, config_data: Dict[str, Any]) -> FrameworkConfig:
        """解析配置数据"""
        try:
            # 解析UBox配置
            ubox_data = config_data.get('ubox', {})
            ubox_config = UBoxConfig(
                secret_id=ubox_data.get('secret_id', ''),
                secret_key=ubox_data.get('secret_key', ''),
                mode=ubox_data.get('mode', RunMode.NORMAL)
            )

            # 解析测试配置
            test_data = config_data.get('test', {})
            test_config = TestConfig(
                test_name=test_data.get('test_name', 'default_test'),
                test_description=test_data.get('test_description', ''),
                screenshot_on_failure=test_data.get('screenshot_on_failure', True),
                screenshot_on_success=test_data.get('screenshot_on_success', False),
                selected_tests=test_data.get('selected_tests', None),
            )

            # 解析任务配置
            task_data = config_data.get('task', {})
            task_config = TaskConfig(
                job_id=task_data.get('job_id', ''),
                serial_num=task_data.get('serial_num', ''),
                os_type=task_data.get('os_type', 'android'),
                app_name=task_data.get('app_name', ''),
                auth_code=task_data.get('auth_code')
            )

            # 解析报告配置
            report_data = config_data.get('report', {})
            report_config = ReportConfig(
                report_format=report_data.get('report_format', 'excel'),
                output_dir=report_data.get('output_dir', './test_result/log'),
                chart_quality=report_data.get('chart_quality', 'high'),
                theme=report_data.get('theme', 'default'),
            )

            # 创建框架配置
            framework_config = FrameworkConfig(
                ubox=ubox_config,
                device=DeviceConfig(),
                test=test_config,
                task=task_config,
                report=report_config,
                log_level=config_data.get('log_level', 'INFO'),
            )

            return framework_config

        except Exception as e:
            raise ValueError(f"配置解析失败: {e}\n{traceback.format_exc()}")

    def save_config(self, config: FrameworkConfig, output_path: str) -> None:
        """
        保存配置到文件
        
        Args:
            config: 要保存的配置对象
            output_path: 输出文件路径
        """
        config_dict = {
            'ubox': {
                'secret_id': config.ubox.secret_id,
                'secret_key': config.ubox.secret_key,
                'mode': config.ubox.mode.value if hasattr(config.ubox.mode, 'value') else str(config.ubox.mode)
            },
            'test': {
                'test_name': config.test.test_name,
                'test_description': config.test.test_description,
                'screenshot_on_failure': config.test.screenshot_on_failure,
                'screenshot_on_success': config.test.screenshot_on_success,
                'selected_tests': config.test.selected_tests
            },
            'task': {
                'job_id': config.task.job_id,
                'serial_num': config.task.serial_num,
                'os_type': config.task.os_type,
                'app_name': config.task.app_name,
                'auth_code': config.task.auth_code
            },
            'report': {
                'report_format': config.report.report_format,
                'output_dir': config.report.output_dir,
                'chart_quality': config.report.chart_quality,
                'theme': config.report.theme
            },
            'log_level': config.log_level
        }

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                if output_path.endswith('.yaml') or output_path.endswith('.yml'):
                    yaml.dump(config_dict, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
                else:
                    json.dump(config_dict, f, indent=2, ensure_ascii=False)

        except Exception as e:
            raise ValueError(f"配置保存失败: {e}\n{traceback.format_exc()}")

    def get_config(self) -> FrameworkConfig:
        """获取当前配置"""
        if self._config is None:
            self._config = self.load_config()
        return self._config

    def validate_task_config(self) -> bool:
        """
        验证任务配置是否完整
        
        Returns:
            bool: 配置是否有效
        """
        config = self.get_config()
        task = config.task

        if not task.serial_num:
            logger.error("设备序列号不能为空")
            return False

        if not task.app_name:
            logger.error("应用包名不能为空")
            return False

        # 验证操作系统类型
        valid_os_types = ['android', 'ios', 'hm']
        if task.os_type.lower() not in valid_os_types:
            logger.error(f"不支持的操作系统类型: {task.os_type}")
            return False

        return True

    def update_config(self, job_id: str, serial_num: str, os_type: str,
                      app_name: str, mode: RunMode, auth_code: Optional[str] = None) -> None:
        """
        更新任务参数
        
        Args:
            job_id: 任务ID
            serial_num: 设备序列号
            os_type: 操作系统类型
            app_name: 应用包名
            mode: 运行模式 (normal/local)
            auth_code: 设备认证码
        """
        config = self.get_config()
        config.task.job_id = job_id
        config.task.serial_num = serial_num
        config.task.os_type = os_type
        config.task.app_name = app_name
        config.task.auth_code = auth_code
        config.ubox.mode = mode

        # 保存更新后的配置
        self.save_config(config, self.config_path)
