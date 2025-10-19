# pylint: skip-file
"""Host 主机, 用来监控设备端 secs服务发上来的数据, 然后处理后再发给工厂."""
import collections
import logging
from typing import Callable, Union

from secsgem.secs.variables import Array, String, U4
from secsgem import hsms, gem

from passive_server import factory, secs_config



class ActiveHost:
    """ActiveHost class."""

    def __init__(self, passive_ips: list[str]):
        """ActiveHost 构造函数.

        Args:
            passive_ips: 要监控设备 secs 服务的 ip 和 端口列表.
        """
        self.logger = logging.getLogger("ActiveHost")
        self.passive_ips = passive_ips
        self._host_handlers = {}
        self._create_gem_host_handler()

    @property
    def host_handlers(self) -> dict[str, gem.GemHostHandler]:
        """监控设备 secs 服务的 GemHostHandler 实例字典."""
        return self._host_handlers

    def _create_gem_host_handler(self):
        """根据配置文件创建连接设备的客户端."""
        for equipment_ip_port in self.passive_ips:
            equipment_ip, port = equipment_ip_port.split(":")
            setting = hsms.HsmsSettings(
                address=equipment_ip,
                port=int(port),
                connect_mode=getattr(hsms.HsmsConnectMode, "ACTIVE"),
                device_type=hsms.DeviceType.HOST
            )
            host_handler = gem.GemHostHandler(setting)
            self._host_handlers[equipment_ip_port] = host_handler
            self.report_link_sv_or_dv(host_handler, equipment_ip, port)

    @staticmethod
    def report_link_sv_or_dv(host_handler: gem.GemHostHandler, equipment_ip: str, port: str):
        """将报告和 sv 或 dv 关联.

        Args:
            host_handler: GemHostHandler 实例.
            equipment_ip: host监控设备的 secs 服务 ip.
            port: host监控设备的 secs 服务端口.
        """
        mysql = factory.get_mysql_instance(equipment_ip, f"{equipment_ip}:{port}")
        report_link_list = secs_config.get_report_link_info(mysql)
        for report_link in report_link_list:
            host_handler.report_subscriptions.update(report_link)

    def enable_host_handler(self):
        """启动监控设备 secs 服务的客户端"""
        for equipment_ip_port, host_handler in self._host_handlers.items():
            host_handler.enable()
            self.logger.info("已启动监控 %s 设备 secs 服务的 Active 客户端", equipment_ip_port)

    def set_call_back(self, ip_port: str, func_name: str, func: Callable):
        """设置监控到设备上报数据触发的回调函数.

        Args:
            ip_port: 监控的设备服务端的 ip port.
            func_name: 函数名称.
            func: 函数本体.
        """
        setattr(self.get_host_instance(ip_port).callbacks, func_name, func)

    def set_receive_event_callback(self, ip_port: str, func: Callable):
        """设置监控到设备上事件据触发的回调函数.

        Args:
            ip_port: 监控的设备服务端的 ip port.
            func: 函数本体.
        """
        host_handler = self.get_host_instance(ip_port)
        host_handler.protocol.events.collection_event_received += func

    def get_host_instance(self, ip_port: str) -> gem.GemHostHandler:
        """获取监控设备 secs 服务的 GemHostHandler.

        Args:
            ip_port: 监控设备 secs 服务的 ip 和 端口.

        Returns:
            gem.GemHostHandler: 返回 gem.GemHostHandler.
        """
        return self._host_handlers[ip_port]


    def send_s2f41(self, ip_port: str, rcmd: str, params_dict: Union[list[str], dict]):
        """给指定设备的 secs 服务下发 s2f41.

        Args:
            rcmd: 远程命令名称.
            params_dict: 远程命令参数字典.
            ip_port: 指定设备的 secs 服务的 ip 和端口.
        """
        params_dict_send = collections.OrderedDict()
        for param in params_dict:
            param_value = params_dict[param]
            if isinstance(param_value, list):
                if isinstance(param_value[0], str):
                    params_dict_send[param] = Array(String,param_value)
                elif isinstance(param_value[0], int):
                    params_dict_send[param] = Array(U4, param_value)
            else:
                params_dict_send[param] = param_value

        host_handler = self.get_host_instance(ip_port)
        host_handler.send_remote_command(rcmd, params_dict_send)
