"""
SuperCode 核心编译器
包含 main 函数
"""

import re

class SuperCodeError(Exception):
    """SuperCode 基础异常类"""
    pass

class CompilationError(SuperCodeError):
    """编译错误异常类"""
    pass

class Token:
    def __init__(self, type, value, line):
        self.type = type
        self.value = value
        self.line = line

class Lexer:
    def __init__(self, code):
        self.code = code
    
    def tokenize(self):
        tokens = []
        lines = self.code.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            line = line.rstrip()
            if line.strip():
                tokens.append(Token('LINE', line, line_num))
        
        return tokens

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
    
    def parse(self):
        statements = []
        for token in self.tokens:
            content = token.value
            
            # 检测函数调用语法：函数名(参数)
            function_call_match = re.match(r'(\w+)\(([^)]*)\)', content.strip())
            
            if function_call_match:
                # 函数调用格式
                func_name = function_call_match.group(1)
                args_str = function_call_match.group(2)
                # 分割参数（支持逗号分隔或空格分隔）
                args = [arg.strip() for arg in re.split(r'[,\s]+', args_str) if arg.strip()]
                
                statements.append({
                    'type': 'function_call',
                    'content': content,
                    'line': token.line,
                    'indent': len(content) - len(content.lstrip()),
                    'func_name': func_name,
                    'args': args
                })
            else:
                # 传统命令格式
                statements.append({
                    'type': 'raw_line',
                    'content': content,
                    'line': token.line,
                    'indent': len(content) - len(content.lstrip())
                })
        
        return statements

class Compiler:
    def __init__(self):
        self.functions = {}
        self.block_handlers = {}
    
    def set_func(self, name, func):
        self.functions[name] = func
        return self
    
    def set_block_handler(self, keyword, handler):
        self.block_handlers[keyword] = handler
        return self
    
    def compile(self, code):
        lexer = Lexer(code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        statements = parser.parse()
        
        results = []
        i = 0
        while i < len(statements):
            statement = statements[i]
            result, skip_lines = self._execute_free(statement, statements, i)
            if result is not None:
                results.append(result)
            i += skip_lines + 1
        
        return results
    
    def _execute_free(self, statement, all_statements, current_index):
        line_content = statement['content'].strip()
        
        # 检查是否是函数调用格式
        if statement['type'] == 'function_call':
            func_name = statement['func_name']
            args = statement['args']
            
            # 检查块处理器
            block_handler = self.block_handlers.get(func_name)
            if block_handler:
                return block_handler(args, all_statements, current_index, self)
            
            # 检查普通函数
            func = self.functions.get(func_name)
            if func:
                try:
                    return func(*args), 0
                except Exception as e:
                    return f"Error calling {func_name}: {e}", 0
            
            return f"Unknown function: {func_name}", 0
        
        else:
            # 原有的空格分割逻辑
            parts = line_content.split()
            if not parts:
                return None, 0
            
            first_word = parts[0]
            rest = parts[1:]
            
            # 检查块处理器
            block_handler = self.block_handlers.get(first_word)
            if block_handler:
                return block_handler(rest, all_statements, current_index, self)
            
            # 检查普通函数
            func = self.functions.get(first_word)
            if func:
                try:
                    return func(*rest), 0
                except:
                    return func(line_content), 0
            
            print(f"执行: {line_content}")
            return None, 0

def safe_eval(expression, functions=None):
    """
    安全计算表达式，支持：
    - 数字：123, 3.14
    - 字符串："hello", 'world'
    - 数学算式：2 + 3 * 4
    - 注册的函数调用：add(1, 2)
    
    参数：
        expression: 要计算的表达式字符串
        functions: 函数字典，用于解析函数调用
    
    返回：
        计算结果
    """
    if functions is None:
        functions = {}
    
    # 去除前后空格
    expr = expression.strip()
    
    # 1. 检查是否是字符串（带引号）
    if (expr.startswith('"') and expr.endswith('"')) or (expr.startswith("'") and expr.endswith("'")):
        return expr[1:-1]  # 返回去掉引号的字符串
    
    # 2. 检查是否是数字
    try:
        if '.' in expr:
            return float(expr)  # 浮点数
        else:
            return int(expr)    # 整数
    except ValueError:
        pass
    
    # 3. 检查是否是函数调用
    func_call_match = re.match(r'(\w+)\(([^)]*)\)', expr)
    if func_call_match:
        func_name = func_call_match.group(1)
        args_str = func_call_match.group(2)
        
        if func_name in functions:
            # 解析参数
            args = []
            if args_str.strip():
                # 分割参数并递归计算每个参数
                raw_args = [arg.strip() for arg in re.split(r',', args_str) if arg.strip()]
                for arg in raw_args:
                    args.append(safe_eval(arg, functions))
            
            # 调用函数
            func = functions[func_name]
            try:
                return func(*args)
            except Exception as e:
                return f"Error in {func_name}: {e}"
        else:
            return f"Unknown function: {func_name}"
    
    # 4. 检查是否是数学表达式（只包含数字和运算符）
    if all(c in '0123456789+-*/.() ' for c in expr):
        try:
            # 使用 eval 但限制在数学表达式
            return eval(expr)
        except:
            return f"Math error: {expr}"
    
    # 5. 检查是否是变量名（在 functions 中查找）
    if expr in functions:
        return functions[expr]()
    
    # 6. 无法解析，返回原字符串
    return expr

# 便捷函数
def set_func(name, func):
    """创建函数配置"""
    def config(compiler):
        compiler.set_func(name, func)
    return config

def set_block_handler(keyword, handler):
    """创建块处理器配置"""
    def config(compiler):
        compiler.set_block_handler(keyword, handler)
    return config

def Compiler_Code(code):
    """快速编译代码的便捷函数"""
    return Compiler().compile(code)

def main():
    """
    SuperCode 主函数 - 演示程序
    用户可以通过命令行直接运行: supercode
    """
    print("🚀 SuperCode Demo")
    print("=" * 40)
    
    # 创建编译器并配置演示功能
    compiler = Compiler()
    
    # 注册演示函数
    compiler.set_func("assign", lambda var, value: f"Set {var} = {value}")
    compiler.set_func("calc", lambda expr: f"Calculation: {expr} = {safe_eval(expr, compiler.functions)}")
    compiler.set_func("show", lambda msg: f"Show: {msg}")
    compiler.set_func("double", lambda x: x * 2)
    compiler.set_func("add", lambda a, b: a + b)
    
    # 演示代码
    demo_code = '''
show Welcome to SuperCode!
show Testing traditional syntax:
assign x 10
calc 2 + 3 * 4
show Testing function call syntax:
calc double(5)
calc add(3, 4)
show Demo completed!
'''
    
    print("Running demo code...")
    print()
    
    results = compiler.compile(demo_code)
    for result in results:
        if result:
            print(result)
    
    print()
    print("🎉 Demo completed!")

if __name__ == "__main__":
    main()