from abc import ABC, abstractmethod


class BaseWriter(ABC):
    """
    数据写入器的抽象基类。
    所有自定义写入器（如CSVWriter, MongoWriter等）都应继承此类并实现 upsert_batch 方法。
    """
    @abstractmethod
    def upsert_batch(self, data_list: list[dict[str, any]], table_name: str, test: bool) -> bool:
        """
        将一批处理好的数据写入目标。

        Args:
            data_list (List[Dict[str, Any]]): 包含多条记录的字典列表。
            table_name (str): 目标（如表名、文件名等）的标识符。

        Returns:
            bool: 写入成功返回True，否则返回False。
            :param data_list:
            :param table_name:
            :param test:
        """
        pass

    def upsert_single(self, data_dict: dict[str, any], table_name: str, test: bool = False) -> bool:
        """
        单行恢复模式
        :param data_dict: 单条字典
        :param table_name: 表名
        :param test:
        :return:
        """
        pass