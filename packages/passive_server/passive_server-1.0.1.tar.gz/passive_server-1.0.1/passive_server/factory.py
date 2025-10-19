# pylint: skip-file
"""生成实例的方法集合."""
import os
from logging.handlers import TimedRotatingFileHandler
from typing import Union

from inovance_tag.tag_communication import TagCommunication
from mitsubishi_plc.mitsubishi_plc import MitsubishiPlc
from modbus_api.modbus_api import ModbusApi
from mysql_api.mysql_database import MySQLDatabase
from secsgem.common import DeviceType
from secsgem.hsms import HsmsSettings, HsmsConnectMode
from siemens_plc.s7_plc import S7PLC
from socket_cyg.socket_server_asyncio import CygSocketServerAsyncio

from passive_server import models_class, common_func, active_host


def get_mysql_instance(host_ip: str, database_name: str, user_name: str = "cyg", password: str = "liuwei.520") -> MySQLDatabase:
    """获取数据库实例对象.

     Args:
         host_ip: 要连接的数据库 ip.
         database_name: 数据库名称.
         user_name: 用户名.
         password: 密码.

    Returns:
        MySQLDatabase: 返回 secs 数据库实例对象.
    """
    return MySQLDatabase(user_name, password, database_name=database_name, host=host_ip)


def get_mysql_secs() -> MySQLDatabase:
    """获取 secs 数据库实例对象.

    Returns:
        MySQLDatabase: 返回 secs 数据库实例对象.
    """
    return MySQLDatabase("root", "liuwei.520")


def get_socket_server():
    """获取 socket 服务端示例"""
    return CygSocketServerAsyncio("127.0.0.1", 1830)


def get_hsms_setting() -> HsmsSettings:
    """获取 HsmsSettings 实例对象.

    Returns:
        HsmsSettings: 返回 HsmsSettings 实例对象.
    """
    mysql = get_mysql_secs()
    secs_ip = mysql.query_data(models_class.EcList, {"ec_name": "secs_ip"})[0].get("value", "127.0.0.1")
    secs_port = mysql.query_data(models_class.EcList, {"ec_name": "secs_port"})[0].get("value", 5000)
    hsms_settings = HsmsSettings(
        address=secs_ip, port=int(secs_port),
        connect_mode=getattr(HsmsConnectMode, "PASSIVE"),
        device_type=DeviceType.EQUIPMENT
    )

    return hsms_settings


def get_time_rotating_handler() -> TimedRotatingFileHandler:
    """获取自动生成日志的日志器实例.

    Returns:
        TimedRotatingFileHandler: 返回自动生成日志的日志器实例.
    """
    return TimedRotatingFileHandler(
        f"{os.getcwd()}/log/all.log",
        when="D", interval=1, backupCount=10, encoding="UTF-8"
    )


def get_active_host_instance() -> active_host.ActiveHost:
    """获取 ActiveHost 实例.

    Returns:
        ActiveHost: 返回 ActiveHost 实例.
    """
    mysql = get_mysql_secs()
    passives_ip_ports_str = mysql.query_data(models_class.EcList, {"ec_name": "low_ip_port_list"})[0].get("value", [])
    passives_ip_port_list = common_func.parse_value(passives_ip_ports_str, "ARRAY")
    return active_host.ActiveHost(passives_ip_port_list)


def get_plc_instance() -> Union[S7PLC, MitsubishiPlc, ModbusApi, TagCommunication]:
    """获取设备端 passive server 实例.

    Returns:
        Union[S7PLC, MitsubishiPlc, ModbusApi, TagCommunication]: 返回 plc 实例对象.
    """
    mysql = get_mysql_secs()
    equipment_name = mysql.query_data(models_class.EcList, {"ec_name": "equipment_name"})[0]["value"]
    plc_ip = mysql.query_data(models_class.EcList, {"ec_name": "plc_ip"})[0]["value"]
    if "snap7" in equipment_name:
        plc = S7PLC(plc_ip)
    elif "tag" in equipment_name:
        plc = TagCommunication(plc_ip)
    elif "modbus" in equipment_name:
        plc = ModbusApi(plc_ip)
    else:
        plc_port = mysql.query_data(models_class.EcList, {"ec_name": "plc_port"})[0]["value"]
        plc = MitsubishiPlc(plc_ip, plc_port)
    return plc
