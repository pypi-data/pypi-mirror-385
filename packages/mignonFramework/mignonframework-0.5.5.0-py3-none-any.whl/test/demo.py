from mignonFramework import SQLiteTracker, TableId , VarChar, injectSQLite
from typing import List
import os
if __name__ == "__main__":

    # --- 1. 定义数据模型 ---
    @TableId('id')
    @VarChar("name", 50)
    class User:
        id: int
        name: str
        age: int

        # 为了方便创建实例
        def __init__(self, id: int, name: str, age: int):
            self.id = id
            self.name = name
            self.age = age

    DB_FILE = "./test_slicing.db"

    # 每次运行时清理旧的数据库文件，保证测试环境纯净
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
        print(f"已删除旧的数据库文件: {DB_FILE}")

    # --- 2. 设置 SQLiteTracker 和配置类 ---
    db_manager = SQLiteTracker(db_path=DB_FILE)

    @injectSQLite(db_manager)
    class AppConfig:
        users: List[User]
        small_list: List[User] # 用于测试数据不足的情况

    # --- 3. 准备数据 ---
    config = AppConfig()
    users_proxy = config.users
    small_list_proxy = config.small_list

    # 插入15条数据到 users 代理列表
    print("\n正在向 'users' 列表插入15条数据...")
    for i in range(15):
        users_proxy.append(User(id=i, name=f"User_{i}", age=20 + i))
    print("数据插入完成。")

    # 插入4条数据到 small_list 代理列表
    print("\n正在向 'small_list' 列表插入4条数据...")
    for i in range(4):
        small_list_proxy.append(User(id=i, name=f"Small_{i}", age=50 + i))
    print("数据插入完成。")

    # --- 4. 执行测试 ---
    def run_test(description, code_str):
        print(f"\n--- {description} ---")
        print(f"执行: print({code_str})")
        try:
            result = eval(code_str)
            print(f"结果: {result}")
            print(f"类型: {type(result)}")
            if isinstance(result, list):
                print(f"长度: {len(result)}")
        except Exception as e:
            print(f"错误: {type(e).__name__}: {e}")

    print("\n" + "="*20 + " 开始对 users 列表 (15条数据) 进行测试 " + "="*20)
    run_test("1. 测试列表长度", "len(users_proxy)")
    run_test("2. 测试正向索引 users_proxy[0]", "users_proxy[0]")
    run_test("3. 测试负向索引 users_proxy[-1]", "users_proxy[-1]")
    run_test("4. 测试基本切片 users_proxy[2:5]", "users_proxy[2:5]")
    run_test("5. 【重点】测试负向切片 users_proxy[-10:] (数据充足)", "users_proxy[-10:]")
    run_test("6. 测试切片到末尾 users_proxy[12:]", "users_proxy[12:]")
    run_test("7. 测试从头切片 users_proxy[:3]", "users_proxy[:3]")
    run_test("8. 测试完整切片(复制) users_proxy[:]", "users_proxy[:]")
    run_test("9. 测试带正步长的切片 users_proxy[1:10:2]", "users_proxy[1:10:2]")
    run_test("10. 【重点】测试反向切片(反转) users_proxy[::-1]", "users_proxy[::-1]")
    run_test("11. 测试复杂的反向切片 users_proxy[10:2:-2]", "users_proxy[10:2:-2]")
    run_test("12. 【重点】测试结果为空的切片 users_proxy[5:2]", "users_proxy[5:2]")
    run_test("13. 测试越界索引 users_proxy[99]", "users_proxy[99]")

    print("\n" + "="*20 + " 开始对 small_list 列表 (4条数据) 进行测试 " + "="*20)
    run_test("14. 【重点】测试负向切片 small_list_proxy[-10:] (数据不足)", "small_list_proxy[-10:]")
    run_test("15. 测试负向切片 small_list_proxy[-4:] (数据刚好)", "small_list_proxy[-4:]")

    print(f"\n测试完成。您可以检查当前目录下的数据库文件: {DB_FILE}")