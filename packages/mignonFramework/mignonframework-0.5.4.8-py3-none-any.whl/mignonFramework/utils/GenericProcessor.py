import json as std_json
import os
import sys
import io
import re
from contextlib import redirect_stdout
from datetime import datetime
from typing import Dict, Callable, List, Optional, Any, Set, Tuple

from mignonFramework.utils.writer.MySQLManager import MysqlManager
from mignonFramework.utils.config.ConfigReader import ConfigManager
from mignonFramework.utils.writer.BaseWriter import BaseWriter
from mignonFramework.utils.reader.BaseReader import BaseReader
from mignonFramework.utils.reader.JSONLineReader import JsonLineReader


class CallbackException(Exception):
    """当用户提供的回调函数中发生异常时抛出，用于区分框架内部错误。"""
    pass


class Rename:
    """一个辅助类，在modifier_function中用于明确表示重命名操作。"""

    def __init__(self, new_key_name: str):
        self.new_key_name = new_key_name


class GenericFileProcessor:
    """
    一个通用的、可定制的逐行文件处理器，用于将文件内容批量写入指定目标。
    支持零配置启动、交互式的Eazy Mode和行级错误处理。
    """

    def __init__(self,
                 path: str,
                 reader: Optional[BaseReader] = None,
                 writer: Optional[BaseWriter] = None,
                 table_name: Optional[str] = None,
                 modifier_function: Optional[Callable[[Dict], Dict]] = None,
                 filter_function: Optional[Callable[[Dict, int], bool]] = None,
                 exclude_keys: Optional[List[str]] = None,
                 include_keys: Optional[List[str]] = None,
                 default_values: Optional[Dict[str, Any]] = None,
                 batch_size: int = 1000,
                 callBack: Optional[Callable[[bool, List[Dict], str, Optional[int]], None]] = None,
                 print_mapping_table: bool = True,
                 on_error: str = 'stop',
                 eazy: bool = False,
                 auto_skip_error: bool = False):
        self.is_ready = True
        self.config_manager = ConfigManager(filename='./resources/config/generic.ini', section='GenericProcessor')
        self.test = False
        self.eazy = eazy
        if not reader:
            reader = JsonLineReader(path)
        self.reader = reader
        self.writer = writer
        self.table_name = table_name

        if not self.eazy:
            if self.reader is None or self.writer is None or self.table_name is None:
                self._init_from_config()
            if not self.is_ready:
                return
            if self.writer and not isinstance(self.writer, BaseWriter):
                raise TypeError("writer 必须是 BaseWriter 的一个实例。")
            if self.reader and not isinstance(self.reader, BaseReader):
                raise TypeError("reader 必须是 BaseReader 的一个实例。")
        else:
            if self.reader is None:
                self._init_from_config()
            self.is_ready = True

        self.modifier_function = modifier_function
        self.filter_function = filter_function
        self.exclude_keys = set(exclude_keys) if exclude_keys else set()
        self.include_keys = set(include_keys) if include_keys else None
        self.default_values = default_values if default_values else {}
        self.batch_size = batch_size
        self.callBack = callBack
        self.print_mapping_table = print_mapping_table
        self.on_error = on_error
        self.auto_skip_error = auto_skip_error

    def _init_from_config(self):
        config_data = self.config_manager.getAllConfig()
        config_incomplete = False

        if self.reader is None:
            path_from_config = config_data.get('path')
            if path_from_config and 'YOUR_' not in str(path_from_config):
                try:
                    self.reader = JsonLineReader(path=path_from_config)
                except FileNotFoundError as e:
                    print(f"[ERROR] 配置文件中的路径无效: {e}")
                    self.is_ready = False
                    config_incomplete = True
            else:
                config_incomplete = True

        if self.writer is None:
            db_keys = ['host', 'user', 'password', 'database', 'port']
            if config_data and all(config_data.get(k) and 'YOUR_' not in str(config_data.get(k)) for k in db_keys):
                db_config = {k: config_data[k] for k in db_keys}
                db_config['port'] = int(db_config.get('port', 3306))
                try:
                    self.writer = MysqlManager(**db_config)
                    if not self.writer.is_connected():
                        raise ConnectionError("数据库连接测试失败，请检查配置和网络状态。")
                except Exception as e:
                    print(f"[ERROR] 初始化数据库连接时发生致命错误: {e}")
                    raise ConnectionError(f"无法连接到数据库: {e}") from e
            else:
                config_incomplete = True

        if self.table_name is None:
            if not (config_data and config_data.get('table_name') and 'YOUR_' not in str(
                    config_data.get('table_name'))):
                config_incomplete = True
            else:
                self.table_name = config_data['table_name']

        if config_incomplete:
            self._guide_user_to_config()
            self.is_ready = False

    def _guide_user_to_config(self):
        print("\n" + "=" * 60)
        print("处理器检测到配置不完整，将为您创建或更新配置文件。")
        print(f"配置文件路径: {os.path.abspath('./resources/config/generic.ini')}")
        placeholders = {'host': 'YOUR_DATABASE_HOST', 'user': 'YOUR_USERNAME', 'password': 'YOUR_PASSWORD',
                        'database': 'YOUR_DATABASE_NAME', 'port': '3306', 'table_name': 'YOUR_TARGET_TABLE',
                        'path': 'PATH_TO_YOUR_FILE_OR_DIRECTORY'}
        for key, value in placeholders.items():
            if not self.config_manager.getConfig(key) or 'YOUR_' in str(self.config_manager.getConfig(key)):
                self.config_manager.setConfig(key, value)
        print("请填写配置文件中的占位符信息后重新运行。")
        print("=" * 60 + "\n")

    def _start_eazy_mode_server(self, sample_data: Dict[str, Any]):
        try:
            from mignonFramework.utils.eazy_mode_app import EazyAppRunner
        except ImportError as e:
            print(f"[ERROR] 无法启动 Eazy Mode: {e}")
            return
        print("\n" + "=" * 60)
        print("--- Eazy Mode 已启动 ---")
        runner = EazyAppRunner(sample_data=sample_data, to_snake_case_func=self._to_snake_case,
                               pre_default_values=self.default_values)
        runner.run()
        print("--- Eazy Mode 已关闭 ---")
        print("=" * 60 + "\n")

    def _to_snake_case(self, name: str) -> str:
        if not isinstance(name, str) or not name:
            return ""
        name = name.strip('`')
        s1 = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _finalize_types(self, data_dict: dict) -> dict:
        final_data = {}
        for key, value in data_dict.items():
            if value is None or (isinstance(value, str) and value.strip() == ''):
                final_data[key] = None
            elif isinstance(value, (dict, list)):
                final_data[key] = std_json.dumps(value, ensure_ascii=False)
            else:
                final_data[key] = value
        return final_data

    def _process_single_item(self, json_data: dict, temp_exclude_keys: Optional[Set[str]] = None,
                             temp_default_values: Optional[Dict[str, Any]] = None) -> Optional[Dict]:
        current_excludes = self.exclude_keys.union(temp_exclude_keys or set())

        # 应用 default_values
        data_with_defaults = {**json_data}
        for key, default_value in (temp_default_values or self.default_values).items():
            if data_with_defaults.get(key) in (None, ''):
                data_with_defaults[key] = default_value

        processed_data = {}
        # 应用 include_keys 或 exclude_keys
        if self.include_keys is not None:
            for original_key, value in data_with_defaults.items():
                snake_case_key = self._to_snake_case(original_key)
                if snake_case_key in self.include_keys:
                    processed_data[snake_case_key] = value
        else:
            for original_key, value in data_with_defaults.items():
                if original_key not in current_excludes:
                    processed_data[self._to_snake_case(original_key)] = value

        # 应用 modifier_function
        if self.modifier_function:
            try:
                with io.StringIO() as buf, redirect_stdout(buf):
                    patch_dict = self.modifier_function(data_with_defaults)

                # 智能识别被 modifier 显式处理过的键，并更新 processed_data
                for original_src_key, instruction in patch_dict.items():
                    target_key_for_patch = None
                    value_for_patch = None

                    if isinstance(instruction, Rename):
                        target_key_for_patch = instruction.new_key_name
                        value_for_patch = data_with_defaults.get(original_src_key)
                    elif isinstance(instruction, tuple) and len(instruction) == 2:
                        target_key_for_patch, value_for_patch = instruction
                    else:
                        target_key_for_patch = self._to_snake_case(original_src_key)
                        value_for_patch = instruction

                    if target_key_for_patch is not None and (
                            self.include_keys is None or target_key_for_patch in self.include_keys):

                        # 如果原始键被重命名，则移除旧键
                        if target_key_for_patch != self._to_snake_case(original_src_key) and self._to_snake_case(original_src_key) in processed_data:
                            del processed_data[self._to_snake_case(original_src_key)]

                        processed_data[target_key_for_patch] = value_for_patch

            except Exception as e:
                print(f"[ERROR] modifier_function 执行失败: {e}")
                raise CallbackException(f"modifier_function error: {e}") from e

        return self._finalize_types(processed_data)

    def _is_skippable_sql_error(self, exception: Exception) -> bool:
        """
        判断一个异常是否是可跳过的、与单行数据相关的SQL错误。
        :param exception: 捕获到的异常对象。
        :return: 如果是可跳过的数据错误则返回 True，否则返回 False。
        """
        if not hasattr(exception, 'args') or not isinstance(exception.args, tuple):
            return False

        error_message = str(exception).lower()
        skippable_codes = {
            1054, 1062, 1265, 1292, 1366, 1406, 1452,
        }
        fatal_codes = {
            2002, 2003, 2006, 2013,
        }

        code_match = re.search(r"\((\d+),", str(exception))
        if code_match:
            code = int(code_match.group(1))
            if code in skippable_codes:
                return True
            if code in fatal_codes:
                return False

        skippable_keywords = ["duplicate entry", "data too long", "incorrect integer value", "unknown column"]
        if any(keyword in error_message for keyword in skippable_keywords):
            return True

        return False

    def _execute_batch(self, data_tuples: List[Tuple[Dict, int]], filename: str):
        if not data_tuples:
            return
        json_list = [item[0] for item in data_tuples]
        try:
            status = self.writer.upsert_batch(json_list, self.table_name, test=self.test)
            if self.callBack:
                self.callBack(status, json_list, filename, max(item[1] for item in data_tuples))
            return
        except Exception as batch_exception:
            print(f"\n[WARNING] 批量写入失败 (文件: {filename})。错误: {batch_exception}")
            print("--- 即将进入逐行恢复模式 ---")
            for i, (data_dict, line_num) in enumerate(data_tuples):
                try:
                    self.writer.upsert_single(data_dict, self.table_name, test=self.test)
                    if self.callBack:
                        self.callBack(True, [data_dict], filename, line_num)

                except Exception as single_exception:
                    if not self._is_skippable_sql_error(single_exception):
                        print("\n" + "=" * 80)
                        print(f"[FATAL] 遇到不可恢复的错误，程序将终止。")
                        print(f"  - 文件: {filename}\n  - 行号: {line_num}\n  - 错误: {single_exception}")
                        print("=" * 80)
                        raise single_exception

                    print("\n" + "=" * 80)
                    print(
                        f"[ERROR] 定位到错误行!\n  - 文件: {filename}\n  - 行号: {line_num}\n  - 错误: {single_exception}\n  - 数据: {data_dict}")
                    print("=" * 80)

                    if self.auto_skip_error:
                        print(f"  [INFO] 配置了自动跳过，已跳过第 {line_num} 行。")
                        continue
                    try:
                        choice = input("输入 'y' 跳过此行，'s' 跳过本批次剩余所有行，其他任意键将终止程序: ").lower()
                    except EOFError:
                        print("\n  [FATAL] 检测到非交互式环境 (EOFError)，无法请求用户输入。将终止当前文件处理。")
                        raise  # [MODIFIED] Re-raise the EOFError itself to be caught by the outer loop

                    if choice == 'y':
                        print(f"  [INFO] 已跳过第 {line_num} 行。")
                        continue
                    elif choice == 's':
                        print(f"  [INFO] 已跳过批次中剩余的所有行。")
                        break
                    else:
                        print("  [FATAL] 用户选择终止程序。")
                        raise single_exception
            print("--- 逐行恢复模式结束 ---")

    def _get_display_width(self, text: str) -> int:
        width = 0
        for char in text:
            width += 2 if '\u4e00' <= char <= '\u9fff' else 1
        return width

    def _generate_and_print_mapping(self, sample_json: Dict[str, Any]):
        if not sample_json:
            print("\n[WARNING] 无法生成字段映射表，因为未能从文件中抽样到有效数据。")
            return
        print("\n" + "=" * 102)
        print("--- 字段映射对照表 (Field Mapping Table) ---")
        col_widths = (30, 30, 30)
        header = "| {:{w1}} | {:{w2}} | {:{w3}} |".format("原始键 (或推断源)", "目标键", "目标值示例", w1=col_widths[0],
                                                          w2=col_widths[1], w3=col_widths[2])
        print(header)
        print("-" * (sum(col_widths) + 7))

        processed_sample = self._process_single_item(sample_json)
        if not processed_sample:
            print("  [WARNING] 无法从样本数据生成映射表，因为处理后的样本为空或无效。")
            print("=" * 102 + "\n")
            return

        target_to_original_key_map = {self._to_snake_case(k): k for k in sample_json.keys()}
        if self.modifier_function:
            try:
                patch_dict = self.modifier_function(sample_json)
                for src, instr in patch_dict.items():
                    if isinstance(instr, Rename):
                        target_to_original_key_map[instr.new_key_name] = src
                    elif isinstance(instr, tuple) and len(instr) == 2:
                        target_to_original_key_map[instr[0]] = src
            except Exception:
                pass

        for target_key in sorted(processed_sample.keys()):
            original_key = target_to_original_key_map.get(target_key, 'N/A (新/未知源)')
            value_str = str(processed_sample[target_key])
            value_display = (value_str[:25] + '...') if len(value_str) > 25 else value_str
            padding = [w - self._get_display_width(s) for w, s in
                       zip(col_widths, [original_key, target_key, value_display])]
            print(
                f"| {original_key}{' ' * padding[0]} | {target_key}{' ' * padding[1]} | {value_display}{' ' * padding[2]} |")
        print("=" * 102 + "\n")

    def _find_original_key(self, snake_key: str, sample_json: Dict[str, Any]) -> Optional[str]:
        for key in sample_json.keys():
            if self._to_snake_case(key) == snake_key:
                return key
        for original_def_key in self.default_values.keys():
            if self._to_snake_case(original_def_key) == snake_key:
                return original_def_key
        if self.modifier_function:
            temp_data_with_defaults = {**sample_json, **self.default_values}
            try:
                with io.StringIO() as buf, redirect_stdout(buf):
                    patch_dict = self.modifier_function(temp_data_with_defaults)
                for src, instr in patch_dict.items():
                    if isinstance(instr, Rename) and instr.new_key_name == snake_key:
                        return src
                    elif isinstance(instr, tuple) and len(instr) == 2 and instr[0] == snake_key:
                        return src
                    elif not isinstance(instr, (Rename, tuple)) and self._to_snake_case(src) == snake_key:
                        return src
            except Exception:
                pass
        return None

    def _run_test_mode(self):
        print("\n--- 启动测试模式 ---")
        if self.include_keys is not None:
            print("[INFO] 由于 'include_keys' 已指定，测试模式将不会运行。")
            return

        files_to_test = self.reader.get_files()
        if not files_to_test:
            print("[ERROR] Reader 未找到任何文件进行测试。")
            return

        print(f"将从文件 '{os.path.basename(files_to_test[0])}' 中随机抽取样本进行测试...")
        raw_json_batch = self.reader.get_samples(self.batch_size)
        if not raw_json_batch:
            print("[ERROR] 未能在文件中找到或抽取到有效的JSON数据进行测试。")
            return

        print(f"已随机抽取 {len(raw_json_batch)} 条记录进行自检。")
        suggested_excludes, suggested_defaults, attempt = set(), {}, 0
        while True:
            attempt += 1
            print(f"\n--- 第 {attempt} 次尝试 ---")
            prev_excludes_len, prev_defaults_len = len(suggested_excludes), len(suggested_defaults)
            try:
                processed_batch = [item for item in
                                   [self._process_single_item(item, suggested_excludes, suggested_defaults) for item in
                                    raw_json_batch] if item is not None]
                test_data_tuples = [(item, 0) for item in processed_batch]
                self._execute_batch(test_data_tuples, os.path.basename(files_to_test[0]))
                print("  [成功] 当前配置有效，测试通过！")
                break
            except Exception as e:
                error_message = str(e)
                error_code_match = re.search(r"\((\d+),", error_message)
                error_code = int(error_code_match.group(1)) if error_code_match else 0
                if error_code == 1054:  # Unknown column
                    match = re.search(r"Unknown column '(.+?)'", error_message)
                    if match:
                        col = match.group(1)
                        original_key = self._find_original_key(col, raw_json_batch[0])
                        if original_key and original_key not in suggested_excludes:
                            print(f"  [诊断] 发现未知列 '{col}'，对应源字段 '{original_key}'。")
                            suggested_excludes.add(original_key)
                            print(f"  [操作] 将 '{original_key}' 加入建议排除列表。")
                            continue
                if len(suggested_excludes) == prev_excludes_len and len(suggested_defaults) == prev_defaults_len:
                    print(f"  [失败] 无法自动修复，测试中止。最终错误: {e}")
                    break
        print("\n" + "=" * 60)
        print("--- 测试模式总结与配置建议 ---")
        if suggested_excludes:
            print(f"\n建议的 `exclude_keys` 列表:\nexclude_keys = {list(suggested_excludes)}")
        else:
            print("\n未发现需要排除的字段。")
        print("=" * 60 + "\n")

    def run(self, start_line: int = 1, test: bool = False, isAllMapping: bool = False):
        if not self.is_ready:
            print("[INFO] 处理器尚未就绪，请根据提示完成配置后再次运行。")
            return

        if self.eazy:
            if not self.reader or not self.reader.get_files():
                print(f"[ERROR] Eazy Mode 需要一个有效的 Reader 来提取样本数据。")
                return
            print("[INFO] Eazy Mode 正在从文件中随机抽样以构建配置界面...")
            samples = self.reader.get_samples(500)
            composite_sample = {}
            for sample_data in reversed(samples):
                composite_sample.update(sample_data)
            if not composite_sample:
                print("[ERROR] 未能从文件中抽样到有效的JSON数据来启动 Eazy Mode。")
                return
            self._start_eazy_mode_server(composite_sample)
            return

        files_to_process = self.reader.get_files()
        if not files_to_process:
            return

        if isAllMapping:
            if self.include_keys is None:
                print("[ERROR] 启用 isAllMapping 模式时，'include_keys' 参数必须提供。")
                return
            print("\n--- 启动 'isAllMapping' 模式进行字段映射校验 ---")
            raw_json_samples = self.reader.get_samples(sample_size=max(self.batch_size * 5, 1000))
            if not raw_json_samples:
                print("[ERROR] 未能在文件中找到或抽取到有效的JSON数据进行映射校验。")
                return
            print(f"已抽取 {len(raw_json_samples)} 条记录进行映射校验。")
            found_mapped_keys = set()
            for sample_item in raw_json_samples:
                if processed_item := self._process_single_item(sample_item):
                    found_mapped_keys.update(processed_item.keys())

            missing_include_keys = set(self.include_keys) - found_mapped_keys
            if not missing_include_keys:
                print("\n  [成功] 所有 'include_keys' 中的字段都在样本数据中找到了对应的映射！")
            else:
                print("\n  [警告] 以下 'include_keys' 中的字段未能在样本数据中找到对应的映射：")
                for key in sorted(list(missing_include_keys)):
                    print(f"    - {key}")
            print("\n--- 'isAllMapping' 校验完成 ---")
            return

        self.test = test
        if test:
            self._run_test_mode()
            return

        if self.print_mapping_table:
            print("[INFO] 正在抽样以生成字段映射表...")
            samples = self.reader.get_samples(100)
            composite_sample = {}
            for sample in reversed(samples):
                composite_sample.update(sample)
            self._generate_and_print_mapping(composite_sample)

        print(f"\n--- 开始处理路径: {self.reader.path} ---")
        print(f"发现 {len(files_to_process)} 个文件待处理...")
        for i, file_path in enumerate(files_to_process):
            filename = os.path.basename(file_path)
            print(f"\n[{i + 1}/{len(files_to_process)}] 正在处理: {filename}")
            try:
                data_tuples: List[Tuple[Dict, int]] = []
                total_lines = self.reader.get_total_items(file_path)

                line_iterator = self.reader.read_file(file_path, start_line)
                line_num = None
                while True:
                    try:
                        json_data, line_num = next(line_iterator)

                        if self.filter_function and not self.filter_function(json_data, line_num):
                            continue
                        if parsed_dic := self._process_single_item(json_data):
                            data_tuples.append((parsed_dic, line_num))

                        if total_lines > 0:
                            bar = '█' * int(40 * line_num / total_lines) + '-' * (40 - int(40 * line_num / total_lines))
                            sys.stdout.write(
                                f'\r|{bar}| {line_num / total_lines:.1%} ({line_num}/{total_lines})  本批: [{len(data_tuples)}/{self.batch_size}]')
                            sys.stdout.flush()

                        if len(data_tuples) >= self.batch_size:
                            self._execute_batch(data_tuples, filename)
                            data_tuples = []

                    except StopIteration:
                        break
                    except EOFError:
                        raise
                    except Exception as parse_e:
                        error_msg = f"\n[WARNING] 处理文件 {filename} 第 {line_num} 行时发生错误: {parse_e}"
                        if self.on_error == 'stop':
                            raise
                        if self.on_error == 'log_to_file':
                            with open('error.log', 'a', encoding='utf-8') as err_f:
                                err_f.write(f"{datetime.now()} | {filename} | Line {line_num} | {parse_e}\n")
                        print(error_msg)

                print()
                self._execute_batch(data_tuples, filename)
                print(f"  [成功] 文件已处理。")
            except Exception as e:
                print(f"\n  [失败] 处理文件 {filename} 时发生致命错误: {e}。")
                raise e
        print("\n--- 所有任务处理完成 ---")

