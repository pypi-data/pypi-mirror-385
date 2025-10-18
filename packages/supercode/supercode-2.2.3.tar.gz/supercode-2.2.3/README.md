# SuperCode 🚀

> "为什么写十行代码，当一行就能搞定？" —— SuperCode 的设计哲学

## 这是什么神仙库？🤔

还记得小时候用乐高积木搭房子的快乐吗？SuperCode 就是编程世界里的乐高！它是一个**极简脚本解释器**，让你像搭积木一样写代码。

想象一下，如果你能这样编程：
早上好，打工人！
如果 今天不是周五
喝咖啡 3杯
否则
庆祝 周末快乐！
结束

text

嗯，SuperCode 让你离这个梦想更近一步！

## 安装指南 🛠️

### 正经安装（推荐）
```bash
pip install supercode

5分钟上手 🏃‍
第1分钟：创建你的第一个"对话式"程序
python
from supercode import Compiler, safe_eval

# 创建你的专属AI（假的）
compiler = Compiler()

# 教它说话和计算
compiler.set_func("说", lambda *args: f"🤖: {' '.join(args)}")

def safe_calculate(expression):
    """安全地计算数学表达式"""
    try:
        # 使用 safe_eval 而不是直接 eval
        result = safe_eval(expression, compiler.functions)
        return f"🧮: {expression} = {result}"
    except:
        return f"❌ 计算失败: {expression}"

compiler.set_func("计算", safe_calculate)

# 开始聊天！
code = """
说 你好，我是SuperCode！
计算 2 + 3 * 4
说 看，我会算数学！
"""

results = compiler.compile(code)
for output in results:
    print(output)
输出：

text
🤖: 你好，我是SuperCode！
🧮: 2 + 3 * 4 = 14
🤖: 看，我会算数学！
第2分钟：两种语法，随心切换
SuperCode 支持双语法模式，就像双语切换一样简单：

python
# 传统语法（像说话）
问候 世界
计算 1+1

# 函数语法（像编程）
问候(世界)
计算(1+1)
第3分钟：safe_eval - 你的智能计算器
python
from supercode import safe_eval, Compiler

compiler = Compiler()
compiler.set_func("翻倍", lambda x: x * 2)
compiler.set_func("打招呼", lambda name: f"你好，{name}！")

# 获取函数字典
functions = compiler.functions

# 什么都能算！
test_cases = [
    '123',           # → 123 (数字)
    '"hello"',       # → "hello" (字符串)
    '2 + 3 * 4',     # → 14 (数学)
    '翻倍(5)',       # → 10 (函数调用)
    '打招呼("小明")' # → "你好，小明！" (带参数函数)
]

for expression in test_cases:
    result = safe_eval(expression, functions)
    print(f"{expression} → {result}")
核心功能大全 🎁
🎯 基础命令
python
# 安全显示函数
compiler.set_func("显示", lambda *args: " ".join(args))

# 安全计算函数
def safe_calculator(expression):
    result = safe_eval(expression, compiler.functions)
    return f"计算结果: {result}"

compiler.set_func("计算", safe_calculator)
compiler.set_func("设置", lambda var, value: f"{var} = {value}")
🔄 块处理器（高级玩法）
python
def if_handler(condition, all_statements, current_index, compiler):
    # 使用 safe_eval 评估条件
    condition_result = safe_eval(condition, compiler.functions)
    
    if condition_result:  # 如果条件为真
        # 执行缩进块内的代码
        block_results = []
        # ... 执行逻辑 ...
        return "\n".join(block_results), skip_lines
    
    return None, skip_lines  # 条件不成立，跳过整个块

compiler.set_block_handler("如果", if_handler)
🧩 实际应用场景
场景1：教学工具

python
# 教小朋友编程
compiler.set_func("移动", lambda direction, steps: f"向{direction}移动{steps}步")
compiler.set_func("旋转", lambda angle: f"旋转{angle}度")

program = """
移动 前 5
旋转 90
移动 右 3
"""
场景2：自动化脚本

python
compiler.set_func("读取", lambda file: f"读取文件: {file}")
compiler.set_func("处理", lambda data: f"处理数据: {data}")
compiler.set_func("保存", lambda result: f"保存结果: {result}")
场景3：游戏逻辑

python
compiler.set_func("攻击", lambda target, damage: f"对{target}造成{damage}点伤害")
compiler.set_func("治疗", lambda target, hp: f"治疗{target} {hp}点生命值")
故障排除 🔧
❌ 常见问题1：我的函数不工作！
python
# 错误示范
compiler.set_func("打印", print)  # print返回None，SuperCode会忽略

# 正确做法
compiler.set_func("打印", lambda x: print(x) or f"打印了: {x}")
❌ 常见问题2：数学计算报错
python
# 错误示范
compiler.set_func("算", lambda expr: eval(expr))  # 危险！

# 正确做法
compiler.set_func("算", lambda expr: safe_eval(expr, compiler.functions))
❌ 常见问题3：参数太多或太少
python
# 使用 *args 接收任意参数
compiler.set_func("万能函数", lambda *args: f"收到{len(args)}个参数: {', '.join(args)}")
❌ 常见问题4：块处理器报错
python
# 记住：块处理器必须返回两个值！
def my_handler(args, statements, index, compiler):
    # ...处理逻辑...
    return result, skip_lines  # ← 这个很重要！
性能对比 📊
场景	SuperCode	传统Python	胜负
学习成本	⭐	⭐⭐⭐⭐⭐	🏆
代码行数	少得可怜	多到想哭	🏆
调试难度	几乎为0	头发掉光	🏆
乐趣指数	🚀🚀🚀	😴	🏆
进阶秘籍 🧙‍♂️
秘籍1：创建智能计算器
python
def smart_calculate(expression):
    try:
        result = safe_eval(expression, compiler.functions)
        return f"🎯 {expression} = {result}"
    except Exception as e:
        return f"❌ 计算错误: {e}"

compiler.set_func("算", smart_calculate)
秘籍2：变量系统
python
variables = {}

def store_var(name, value):
    variables[name] = value
    return f"💾 保存 {name} = {value}"

def get_var(name):
    return variables.get(name, "❌ 变量不存在")

compiler.set_func("存", store_var)
compiler.set_func("取", get_var)
秘籍3：循环魔法
python
def loop_handler(times, all_statements, current_index, compiler):
    results = []
    for i in range(int(times[0])):
        results.append(f"第{i+1}次循环")
    return "\n".join(results), skip_lines

compiler.set_block_handler("循环", loop_handler)
命令行玩法 💻
安装后，直接在终端里嗨：

bash
# 运行官方demo
supercode

# 自己写代码测试
python -c "
from supercode import Compiler, safe_eval
c = Compiler()
c.set_func('喊', lambda x: x.upper() + '!!!')
print(c.compile('喊 我爱编程')[0])
"

许可证 📄
MIT License - 翻译成中文就是：随便用，别找我赔钱 😅

<div align="center">
快乐编程，从 SuperCode 开始！ 🎉
如果这个库让你笑了，请给它一个 ⭐
如果这个库帮到你了，请告诉你的朋友
如果这个库让你爱上编程，请感谢当初下载它的自己

</div><p align="center"> <i>记住：编程不应该是一件痛苦的事</i> 💫 </p> ```