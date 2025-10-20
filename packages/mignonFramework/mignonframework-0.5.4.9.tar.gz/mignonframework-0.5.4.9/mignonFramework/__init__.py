"""
这是关于mignon的 Python FrameWork
Queue 顺序打乱器,支持数组或者range
ConfigReader 配置文件读取以及写入
CountLinesInFolder  统计单文件或者文件夹内的行数(支持正则,前缀后缀匹配)
Deduplicate 去重
Logger 日志类
PortForwarding 端口转发
Curl2Request Curl转Request
MysqlManager: 一个健壮的 MySQL 数据库管理器。
GenericFileProcessor: 一个高度通用的文件到数据库ETL（提取、转换、加载）工具。
ProcessFile: 提供一个可配置、可断点续传、高性能的通用文件处理引擎。(默认整文件为json) 它的任务是持续不断地监控一个目录，将文件进行解析、转换，并追加写入到大型结果文件中。
"""
from mignonFramework.utils.utilClass.RunOnce import RunOnce
import mignonFramework.utils.utilClass.color2Logo
import sys
def printLogo():
    is_source_script = sys.argv and sys.argv[0].lower().endswith(('.py', '.pyw'))


    if not is_source_script:
        return

    mignonFrameworkPrint = """                                                         
       __     __)                      \u200ARex
      (, /|  /|   ,                         
        / | / |     _  __   _____
     ) /  |/  |__(_(_/_/ (_(_) / (_
    (_/   '       .-/              
                 (_/               
                                 v 0.5 mignonFramework
    
    """
    print(mignonFramework.utils.utilClass.color2Logo.colorize_logo(mignonFrameworkPrint))
RunOnce.execute(printLogo)
import mignonFramework.utils.BackendAugmentation.RequestsMapping as RequestsMapping
from mignonFramework.utils.Queues import QueueIter, target
from mignonFramework.utils.Logger import Logger
from mignonFramework.utils.config.SQLiteTracker import SQLiteTracker, TableId, injectSQLite, VarChar
from mignonFramework.utils.utilClass.CountLinesInFolder import count_lines_in_single_file as countSingleFileLines, count_lines_in_files as countFolderFileLines, count_lines_in_directory as countDirectoryFileLines
from mignonFramework.utils.utilClass.Deduplicate import deduplicate_file as deduplicateFile, read_and_write_lines as readLines2otherFiles, replace_line_with_file_content as replaceLineByFile, copy_line_by_number as copyLineByNumber
from mignonFramework.utils.utilClass.PortForwarding import start_services as portForwordRun
from mignonFramework.utils.utilClass.Curl2Request import CurlToRequestsConverter as Curl2Request
from mignonFramework.utils.GenericProcessor import GenericFileProcessor as InsertQuick, Rename
from mignonFramework.utils.ProcessFile import run as processRun
from mignonFramework.utils.writer.MySQLManager import MysqlManager
from mignonFramework.utils.reader.BaseReader import BaseReader
from mignonFramework.utils.writer.BaseWriter import BaseWriter
from mignonFramework.utils.config.ConfigReader import ConfigManager
from mignonFramework.utils.config.ConfigReader import inject
from mignonFramework.utils.execJS.execJSTo import execJS
from mignonFramework.utils.mignonFramework_starter import start
from mignonFramework.utils.utilClass.JSONFormatter import JSONFormatter
from mignonFramework.utils.utilClass.SqlDDL2List import extract_column_names_from_ddl as extractDDL2List
from mignonFramework.utils.utilClass.getJSONequals import jsonContrast
from mignonFramework.utils.execJS.MicroserviceByNodeJS import MicroServiceByNodeJS
from mignonFramework.utils.config.JsonlConfigReader import JsonConfigManager, injectJson, ClassKey
from mignonFramework.utils.utilClass.printDirectoryTree import print_directory_tree as printDirectoryTree
from mignonFramework.utils.dataBaseTransfer import DatabaseTransferRunner, AbstractDatabaseTransfer, TransferConfig
from mignonFramework.utils.Louru_Plus import LoguruPlus, SendLog



