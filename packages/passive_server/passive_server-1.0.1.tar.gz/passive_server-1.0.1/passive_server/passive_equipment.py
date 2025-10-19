# pylint: skip-file
"""设备服务端处理器."""
import threading

from typing import Union, Callable
from socket_cyg.socket_server_asyncio import CygSocketServerAsyncio

from passive_server import secs_config, factory, plc_address_operation, passive_server


class EquipmentPassive(passive_server.PassiveServer):
    """EquipmentPassive class."""

    def __init__(self):
        """EquipmentPassive 构造函数."""

        super().__init__()
        self.plc = factory.get_plc_instance()
        self.plc.logger.addHandler(self.file_handler)
        self.plc_type = secs_config.get_plc_type()
        self._monitor_control_thread()

    def _monitor_control_thread(self):
        """监控 plc 的线程."""
        if self.get_ec_value_with_name("is_monitor_plc"):
            self.logger.info("打开监控 plc 的线程.")
            if self.plc.communication_open():
                self.logger.info("首次连接 plc 成功, ip: %s", self.plc.ip)
            else:
                self.logger.info("首次连接 %s plc 失败, ip: %s", self.plc.ip)
            self.__start_monitor_plc_thread()
        else:
            self.logger.info("不打开监控 plc 的线程.")

    def __start_monitor_socket_thread(self, control_instance: CygSocketServerAsyncio, func: Callable):
        """启动 socket 服务.

        Args:
            control_instance: CygSocketServerAsyncio 实例.
            func: 执行操作的函数.
        """
        control_instance.operations_return_data = func
        threading.Thread(target=self.thread_methods.run_socket_server, args=(control_instance,), daemon=True).start()

    def __start_monitor_plc_thread(self):
        """启动监控 plc 的线程."""
        threading.Thread(target=self.thread_methods.mes_heart, daemon=True).start()
        threading.Thread(target=self.thread_methods.control_state, daemon=True).start()
        threading.Thread(target=self.thread_methods.machine_state, daemon=True).start()
        threading.Thread(target=self.thread_methods.current_recipe_id, daemon=True).start()
        for signal_address_info in plc_address_operation.get_signal_address_list():
            if signal_address_info.get("state", False):  # 实时监控的信号才会创建线程
                threading.Thread(
                    target=self.thread_methods.monitor_plc_address, daemon=True,
                    args=(signal_address_info,),
                ).start()

    def get_signal_to_execute_callbacks(self, callbacks: list):
        """监控到信号执行 call_backs.

        Args:
            callbacks: 要执行的流程信息列表.
        """
        for i, callback in enumerate(callbacks, 1):
            description = callback.get("description")
            self.logger.info("%s 第 %s 步: %s %s", "-" * 30, i, description, "-" * 30)

            operation_type = callback.get("operation_type")
            if operation_type == "read":
                self.read_update_sv_or_dv(callback)

            if operation_type == "write":
                self.write_sv_or_dv_value(callback)

            if func_name := callback.get(f"func_name"):
                getattr(self, func_name)(callback)

            self._is_send_event(callback.get("event_id"))
            self.logger.info("%s %s 结束 %s", "-" * 30, description, "-" * 30)

    def read_update_sv_or_dv(self, callback: dict):
        """读取 plc 数据更新 sv 值.

        Args:
            callback: 要执行的 callback 信息.
        """
        sv_or_dv_id = int(callback.get("associate_sv_or_dv"))
        count_num = callback.get("count_num", 1)
        address_info = plc_address_operation.get_address_info(self.plc_type, callback)
        if count_num == 1:
            plc_value = self.plc.execute_read(**address_info)
        else:
            read_multiple_value_func = getattr(self, f"read_multiple_value_{self.plc_type}")
            plc_value = read_multiple_value_func(callback)
        self.set_sv_or_dv_value_with_id(sv_or_dv_id, plc_value)

    def write_sv_or_dv_value(self, callback: dict):
        """向 plc 地址写入 sv 或 dv 值.

        Args:
            callback: 要执行的 callback 信息.
        """
        sv_or_dv_id = int(callback.get("associate_sv_or_dv"))
        count_num = callback.get("count_num", 1)
        value = self.get_sv_or_dv_value_with_id(sv_or_dv_id)
        address_info = plc_address_operation.get_address_info(self.plc_type, callback)
        if count_num == 1:
            self.plc.execute_write(**address_info, value=value)
        else:
            write_multiple_value_func = getattr(self, f"write_multiple_value_{self.plc_type}")
            write_multiple_value_func(callback, value)

        if "snap7" in self.plc_type and address_info.get("data_type") == "bool":
            self.confirm_write_success(address_info, value)  # 确保写入成功

    def read_multiple_value_snap7(self, callback: dict) -> list:
        """读取 Snap7 plc 多个数据.

        Args:
            callback: callback 信息.

        """
        value_list = []
        count_num = callback["count_num"]
        gap = callback.get("gap", 1)
        start_address = int(callback.get("address"))
        for i in range(count_num):
            real_address = start_address + i * gap
            address_info = {
                "address": real_address,
                "data_type": callback.get("data_type"),
                "db_num": self.get_ec_value_with_name("db_num"),
                "size": callback.get("size", 1),
                "bit_index": callback.get("bit_index", 0)
            }
            plc_value = self.plc.execute_read(**address_info)
            value_list.append(plc_value)
            self.logger.info("读取 %s 的值是: %s", real_address, plc_value)
        return value_list

    def read_multiple_value_tag(self, callback: dict) -> list:
        """读取标签通讯 plc 多个数据值.

        Args:
            callback: callback 信息.
        """
        value_list = []
        for i in range(1, callback["count_num"] + 1):
            real_address = callback["address"].replace("$", str(i))
            address_info = {"address": real_address, "data_type": callback["data_type"]}
            plc_value = self.plc.execute_read(**address_info)
            value_list.append(plc_value)
            self.logger.info("读取 %s 的值是: %s", real_address, plc_value)
        return value_list

    def read_multiple_value_modbus(self, callback: dict) -> list:
        """读取 modbus 通讯 plc 多个数据值.

        Args:
            callback: callback 信息.
        """
        value_list = []
        count_num = callback["count_num"]
        start_address = callback.get("address")
        size = callback.get("size")
        for i in range(count_num):
            real_address = start_address + i * size
            address_info = {
                "address": real_address,
                "data_type": callback.get("data_type"),
                "size": size
            }
            plc_value = self.plc.execute_read(**address_info)
            value_list.append(plc_value)
            self.logger.info("读取 %s 的值是: ", real_address, plc_value)
        return value_list

    def write_multiple_value_snap7(self, callback: dict, value_list: list):
        """向 snap7 plc 地址写入多个值.

        Args:
            callback: callback 信息.
            value_list: 写入的值列表.
        """
        gap = callback.get("gap", 1)
        for i, value in enumerate(value_list):
            address_info = {
                "address": int(callback.get("address")) + gap * i,
                "data_type": callback.get("data_type"),
                "db_num": self.get_ec_value_with_name("db_num"),
                "size": callback.get("size", 2),
                "bit_index": callback.get("bit_index", 0)
            }
            self.plc.execute_write(**address_info, value=value)

    def write_multiple_value_tag(self, callback: dict, value_list: list):
        """向汇川 plc 标签通讯地址写入多个值.

        Args:
            callback: callback 信息.
            value_list: 写入的值列表.
        """
        for i, value in enumerate(value_list, 1):
            address_info = {
                "address": callback.get("address").replace("$", str(i)),
                "data_type": callback.get("data_type"),
            }
            self.plc.execute_write(**address_info, value=value)

    def write_multiple_value_modbus(self, callback: dict, value_list: list):
        """向 modbus 通讯地址写入多个值.

        Args:
            callback: callback 信息.
            value_list: 写入的值列表.
        """
        start_address = callback.get("address")
        size = callback.get("size")
        for i, value in enumerate(value_list, 0):
            address_info = {
                "address": int(start_address) + i * size,
                "data_type": callback.get("data_type"),
            }
            self.plc.execute_write(**address_info, value=value)

    def write_clean_signal_value(self, address_info: dict, value: int):
        """向 plc 地址写入清除信号值.

        Args:
            address_info: 要写入的地址信息.
            value: 要写入的值.
        """
        address_info_write = plc_address_operation.get_address_info(self.plc_type, address_info)
        self.plc.execute_write(**address_info_write, value=value)

    def confirm_write_success(self, address_info: dict, value: Union[int, float, bool, str]):
        """向 plc 写入数据, 并且一定会写成功.

        在通过 S7 协议向西门子plc写入 bool 数据的时候, 会出现写不成功的情况, 所以再向西门子plc写入 bool 时调用此函数.
        为了确保数据写入成功, 向任何plc写入数据都可调用此函数, 但是交互的时候每次会多读一次 plc.

        Args:
            address_info: 写入数据的地址位信息.
            value: 要写入的数据.
        """
        while (plc_value := self.plc.execute_read(**address_info)) != value:
            self.logger.warning(f"当前地址 %s 的值是 %s != %s, %s", address_info.get("address"), plc_value,
                                value, address_info.get("description"))
            self.plc.execute_write(**address_info, value=value)

    def set_clear_alarm(self, alarm_code: int):
        """通过S5F1发送报警和解除报警.

        Args:
            alarm_code: 报警 code, 128: 报警, 0: 清除报警.
        """
        address_info = plc_address_operation.get_alarm_address_info(self.plc_type)
        alarm_id = self.plc.execute_read(**address_info, save_log=False)
        self.logger.info("出现报警, 报警id: %s", alarm_id)
        self.send_and_save_alarm(alarm_code, alarm_id)

    def _on_rcmd_pp_select(self, recipe_name: str):
        """工厂切换配方.

        Args:
            recipe_name: 要切换的配方名称.
        """
        pp_select_recipe_name = recipe_name
        self.set_sv_value_with_name("pp_select_recipe_name", pp_select_recipe_name)
        pp_select_recipe_id = secs_config.get_recipe_id_with_name(recipe_name)
        self.set_sv_value_with_name("pp_select_recipe_id", pp_select_recipe_id)

        address_info = plc_address_operation.get_signal_address_info(self.plc_type, "pp_select")
        callbacks = plc_address_operation.get_signal_callbacks(address_info["address"])

        self.get_signal_to_execute_callbacks(callbacks)

        current_recipe_id = self.get_sv_value_with_name("recipe_id")
        current_recipe_name = secs_config.get_recipe_name_with_id(current_recipe_id)
        self.set_sv_value_with_name("recipe_name", current_recipe_name)
        if current_recipe_id == pp_select_recipe_id:
            pp_select_state = 1
        else:
            pp_select_state = 2
        self.set_sv_value_with_name("pp_select_state", pp_select_state)
        self.send_s6f11(2000)

    def _on_rcmd_new_lot(self, lot_name: str, lot_quantity: int):
        """工厂开工单.

        Args:
            lot_name: 工单名称.
            lot_name: 工单数量.
        """
        lot_quantity = int(lot_quantity)
        self.set_sv_value_with_name("lot_name", lot_name)
        self.set_sv_value_with_name("lot_quantity", lot_quantity)
        address_info = plc_address_operation.get_signal_address_info(self.plc_type, "new_lot")
        callbacks = plc_address_operation.get_signal_callbacks(address_info["address"])
        self.get_signal_to_execute_callbacks(callbacks)

    def new_lot_pre_check(self):
        """开工单前检查上个工单是否做完."""
        address_info = plc_address_operation.get_do_quantity_address_info(self.plc_type)
        do_quantity = self.plc.execute_read(**address_info, save_log=True)
        self.set_sv_value_with_name("do_quantity", do_quantity)
        lot_quantity = self.get_sv_value_with_name("lot_quantity")
        if do_quantity < lot_quantity and do_quantity != 0:
            return False
        return True

    async def new_lot(self, lot_info: dict):
        """本地开工单.

        Args:
            lot_info: 工单信息.
        """
        state = self.new_lot_pre_check()
        if not state:
            lot_name = self.get_sv_value_with_name("lot_name")
            lot_quantity = self.get_sv_value_with_name("lot_quantity")
            do_quantity = self.get_sv_value_with_name("do_quantity")
            return f"当前工单 {lot_name} 未生产结束, 不允许开新工单, 应生产: {lot_quantity}, 已生产: {do_quantity}"
        self._on_rcmd_new_lot(lot_info["lot_name"], lot_info["lot_quantity"])
        return f"开工单 {self.get_sv_value_with_name('lot_name')} 成功"
