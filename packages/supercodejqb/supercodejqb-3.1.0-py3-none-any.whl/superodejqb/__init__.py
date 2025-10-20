"""
SuperCode - 简单脚本解释器

一个让编程像说话一样简单的极简脚本解释器。
支持双语法模式、幽默编程风格和强大的表达式解析。
"""

from .core import (
    # 编译器核心
    Compiler,
    Compiler_Code,
    
    # 配置函数
    set_func,
    set_block_handler,
    
    # 主函数和命令行
    main,
    
    # 表达式计算
    safe_eval,
    Cexal,
    
    # 对象系统
    String,
    Int,
    Bool,
    Any,
    string,
    
    # 表达式解析
    expr_format,
    optional,
    r_input,
    endl,
    
    # 类系统
    ClassObject,
    InstanceObject,
    parse_class,
    
    # 条件处理
    h_if,
    
    # 注释处理
    add_comment_handler,
    remove_comments_from_code as remove_comments,
    get_comments_from_code as get_comments,
    enable_comment_processing as enable_comments,
    disable_comment_processing as disable_comments,
    
    # 增强编译器
    EnhancedCompiler,
    
    # 异常类
    SuperCodeError,
    CompilationError
)

# 为对象类创建别名，避免命名冲突
IntObj = Int
BoolObj = Bool
AnyObj = Any

__version__ = "2.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"
__description__ = "A hilarious and simple script interpreter that makes programming as easy as talking"
__url__ = "https://github.com/your-username/supercode"

__all__ = [
    # 编译器核心
    'Compiler',
    'Compiler_Code',
    
    # 配置函数
    'set_func',
    'set_block_handler',
    
    # 主函数和命令行
    'main',
    
    # 表达式计算
    'safe_eval',
    'Cexal',
    
    # 对象系统
    'String',
    'Int',
    'Bool',
    'Any',
    'string',
    'IntObj',
    'BoolObj',
    'AnyObj',
    
    # 表达式解析
    'expr_format',
    'optional',
    'r_input',
    'endl',
    
    # 类系统
    'ClassObject',
    'InstanceObject',
    'parse_class',
    
    # 条件处理
    'h_if',
    
    # 注释处理
    'add_comment_handler',
    'remove_comments',
    'get_comments',
    'enable_comments',
    'disable_comments',
    
    # 增强编译器
    'EnhancedCompiler',
    
    # 异常类
    'SuperCodeError',
    'CompilationError',
    
    # 元数据
    '__version__',
    '__author__',
    '__email__',
    '__description__',
    '__url__'
]

# 便捷导入函数
def create_default_compiler():
    """
    创建带有默认内置函数的编译器实例
    
    返回:
        EnhancedCompiler: 配置好的编译器实例
    """
    return EnhancedCompiler()

def quick_eval(expression):
    """
    快速计算表达式
    
    参数:
        expression: 要计算的表达式字符串
        
    返回:
        计算结果
    """
    return safe_eval(expression)

def quick_compile(code):
    """
    快速编译代码
    
    参数:
        code: 要编译的代码字符串
        
    返回:
        list: 执行结果列表
    """
    compiler = create_default_compiler()
    return compiler.compile(code)

# 版本兼容性
__compatible_python_versions__ = ['3.6', '3.7', '3.8', '3.9', '3.10', '3.11', '3.12']

# 包初始化完成提示
def __initialize_package():
    """包初始化函数"""
    pass

__initialize_package()

# 删除临时变量
del __initialize_package