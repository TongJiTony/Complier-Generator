@echo off
setlocal

:: 获取脚本所在的目录
cd /d %~dp0

:: 设置Python解释器路径（如果需要）
:: set PYTHON_PATH=C:\Path\To\Python\python.exe

:: 运行生成词法分析器的Python脚本
echo Running generate_lexer.py...
%PYTHON_PATH% python generate_lexer.py lexical_spec.txt
if %ERRORLEVEL% neq 0 (
    echo Error occurred while running generate_lexer.py
    exit /b %ERRORLEVEL%
)

:: 运行生成解析器的Python脚本
echo Running generate_parser.py...
%PYTHON_PATH% python generate_parser.py grammar_spec.txt
if %ERRORLEVEL% neq 0 (
    echo Error occurred while running generate_parser.py
    exit /b %ERRORLEVEL%
)

:: 运行编译器的Python脚本
echo Running compiler.py...
%PYTHON_PATH% python compiler.py test_bool.code
if %ERRORLEVEL% neq 0 (
    echo Error occurred while running compiler.py
    exit /b %ERRORLEVEL%
)

echo All scripts ran successfully.
endlocal