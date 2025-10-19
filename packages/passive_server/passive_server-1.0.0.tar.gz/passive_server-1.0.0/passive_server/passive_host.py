# pylint: skip-file
"""Host 的 passive 服务."""
import threading

from secsgem import secs

from passive_server import factory, passive_server


class HostPassive(passive_server.PassiveServer):
    """HostPassive class."""

    def __init__(self) -> None:
        """HostPassive 构造函数."""
        super().__init__()

        self.active_host = factory.get_active_host_instance()
        self._host_thread()

    def _host_thread(self):
        """Host 电脑的线程."""
        self.set_host_callback()
        threading.Thread(target=self.active_host.enable_host_handler, daemon=True).start()

    def set_host_callback(self):
        """设置监控到设备上报数据触发的回调函数."""
        for ip_port in self.active_host.passive_ips:
            for attribute_name in dir(self):
                if attribute_name.startswith("host_callback_"):
                    func_name = attribute_name.split("host_callback_")[-1]
                    self.active_host.set_call_back(ip_port, func_name, getattr(self, attribute_name))
                    self.active_host.set_receive_event_callback(ip_port, self.collection_event_received)

    def collection_event_received(self, data: dict):
        """接收到设备 secs 服务端上报的事件.

        Args:
            data: 事件信息
        """
        variables_value = []
        report_id = data["rptid"]
        ce_id = data["ceid"]
        equipment_info = data["peer"].settings
        self.logger.info("收到设备 %s:%s 上报的 %s 事件", equipment_info.address, equipment_info.port, ce_id)
        variable_values = data["values"]
        self.logger.info("报告 id: %s, 关联变量: %s", report_id, variable_values)
        for variable_info in variable_values:
            for name, value in variable_info.items():
                if name == "value":
                    variables_value.append(value)
        reports = [{"RPTID": report_id, "V": variables_value}]
        self.send_and_waitfor_response(
            self.stream_function(6, 11)({"DATAID": 1, "CEID": ce_id, "RPT": reports})
        )

    def host_callback_alarm_received(self, handler, alarm_id, alarm_code, alarm_text):
        """接收到设备服务端的报警发给工厂.

        Args:
            handler: handler.
            alarm_id: 报警 id.
            alarm_code: 报警 code.
            alarm_text: 报警内容.
        """
        del handler
        self.send_and_waitfor_response(
            self.stream_function(5, 1)({"ALCD": alarm_code, "ALID": alarm_id, "ALTX": alarm_text})
        )
        return secs.data_items.ACKC5.ACCEPTED
