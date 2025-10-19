#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SARM SDK 插件基类

提供可复用的 BasePlugin 抽象类，封装通用的参数解析、日志、客户端初始化、
批处理与统计上报等能力。用户可继承该类实现 extract/transform/load 三个方法。

使用方式：
    from sarm_sdk.plugin import BasePlugin
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from abc import ABC, abstractmethod
from typing import Generator, List, Union, Dict, Optional

from .client_v2 import SARMClientV2 as SARMClient


class BasePlugin(ABC):
    """
    通用插件基类，封装了所有与具体业务无关的底层逻辑。
    """

    # 定义数据上传批次大小
    UPLOAD_BATCH_SIZE = 50
    # 为测试运行定义一个数据处理上限
    TEST_RUN_LIMIT = 10

    def __init__(self):
        self.args = None
        self.config = {}
        self.logger = self._setup_logger()
        self.client = None

    def _setup_logger(self):
        """初始化日志记录器"""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            stream=sys.stdout,
        )
        return logging.getLogger(self.__class__.__name__)

    def _parse_args(self):
        """解析平台运行时传入的参数"""
        parser = argparse.ArgumentParser()
        parser.add_argument("--server_addr", required=True, help="平台服务地址")
        parser.add_argument("--token", required=True, help="平台认证令牌")
        parser.add_argument("--params", default="{}", help="插件配置的JSON字符串")
        parser.add_argument("--factory_id", help="当前执行任务的标识")
        parser.add_argument("--mode", default="running", help="运行模式 (running 或 test)")
        self.args = parser.parse_args()

    def _load_config(self):
        """加载并合并插件配置"""
        try:
            params_data = json.loads(self.args.params)
            if isinstance(params_data, list):
                params_config = {item.get('key'): item.get('value') for item in params_data}
            else:
                params_config = params_data
            self.config.update(params_config)
        except json.JSONDecodeError:
            self.logger.error("无法解析 --params 参数，请检查是否为合法的JSON字符串。")
            raise
        except Exception as e:
            self.logger.error(f"处理 --params 参数时出错: {e}", exc_info=True)
            raise

    def _report_statistics(self, success_count: int, sample_data: List[Dict]):
        """执行完毕后上报统计信息"""
        # 如果没有 factory_id，则跳过统计上报
        if self.args.factory_id is None:
            self.logger.info("未提供 factory_id，跳过统计信息上报。")
            return
            
        self.logger.info("正在上报执行统计信息...")
        
        data_type = self.args.mode
        
        is_test_mode = self.args.mode == 'test'
        
        data_to_report = sample_data if is_test_mode else (sample_data[:1] if sample_data else [])

        statistical_info = {}

        data_key = getattr(self, 'DATA_TYPE_KEY', 'normal')

        statistical_info = {
            data_key: {"count": success_count}
        }
                
        critical_data_count = success_count

        try:
            response = self.client.common.statistics(
                data=data_to_report,
                statistical_info=statistical_info,
                critical_data_count=critical_data_count,
                data_type=data_type
            )
            if response and response.get("code") == 200:
                self.logger.info("统计信息上报成功。")
            else:
                self.logger.error(f"统计信息上报失败: {response}")
        except Exception as e:
            self.logger.error(f"上报统计信息时发生异常: {e}", exc_info=True)

    def run(self):
        """插件主执行入口，包含完整的执行流程"""
        all_successful_data = []
        success_count = 0
        try:
            self._parse_args()
            self._load_config()
            
            client_kwargs = {
                "base_url": self.args.server_addr,
                "token": self.args.token
            }

            # 核心改动：处理 factory_id，并确保其为字符串
            if self.args.factory_id is not None:
                client_kwargs["factory_log_id"] = str(self.args.factory_id)

            # 使用临时配置进行测试
            self.client = SARMClient(**client_kwargs)

            self.logger.info("开始流式处理数据...")
            buffer = []
            error_count = 0
            
            is_test_mode = self.args.mode == 'test'

            for raw_item in self.extract():
                try:
                    transformed_dict = self.transform(raw_item)
                    if transformed_dict is None:
                        continue
                    buffer.append(transformed_dict)
                    all_successful_data.append(transformed_dict)
                    success_count += 1
                except Exception:
                    error_count += 1
                    self.logger.error(
                        "数据转换失败，已跳过。详细错误追溯信息如下:", exc_info=True
                    )
                    self.logger.debug(f"导致失败的原始数据: {raw_item}")
                    continue

                if len(buffer) >= self.UPLOAD_BATCH_SIZE:
                    self.load(buffer)
                    buffer.clear()

                if is_test_mode and success_count >= self.TEST_RUN_LIMIT:
                    self.logger.info(
                        f"[测试运行] 已达到 {self.TEST_RUN_LIMIT} 条数据处理上限，测试提前结束。"
                    )
                    break

            if buffer and not is_test_mode:
                self.load(buffer)

            self.logger.info("插件执行完毕。")
            self.logger.info(f"成功处理: {success_count} 条，失败: {error_count} 条。")

        except Exception as e:
            self.logger.error(f"插件执行过程中发生严重错误，已终止: {e}", exc_info=True)
            sys.exit(1)
        finally:
            if self.client:
                self._report_statistics(success_count, all_successful_data)


    @abstractmethod
    def extract(self) -> Generator[any, None, None]:
        """从数据源提取原始数据。"""
        pass

    @abstractmethod
    def transform(self, raw_item: any) -> Union[Dict, None]:
        """将一条原始数据转换为一个字典。"""
        pass

    @abstractmethod
    def load(self, buffer: List[Dict]):
        """将一个批次的数据上报到平台。"""
        pass


