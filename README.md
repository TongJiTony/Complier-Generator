# Complier-Generator

## Tasks:

利用编译原理课程学习的词法分析器⾃动构造的经典算法、语法分析器⾃动构造的经典算法和中间代码⽣成算法实现⼀个编译器⽣成器(Compiler Generator)。

a. 编译器⽣成器的输⼊为某语⾔的词法规则和语法规则(正规⽂法)，输出为该语⾔的编译器，编译器的输⼊为源代码，输出为正确的中间代码（三地址代码），并对错误的源代码有必要的报错功能

b. 编译器是个⼀遍的编译程序，词法分析程序作为⼦程序，需要的时候被语法分析程序调⽤

c. 使⽤语法制导的翻译技术，在语法分析的同时⽣成中间代码，并保存到⽂件中

## Algorithms:

a. 词法分析：Thompson算法、⼦集法、等价状态法等

b. 语法分析：LR分析法等

c. 中间代码⽣成：属性⽂法、翻译⼦程序等

To do:

1. 属性文法的编写
2. 加入到分析器中
3. complier.py添加翻译模式
   1. 布尔语句
   2. if-else控制语句
   3. while循环语句控制

## Framework from gpto1

1. generate_lexer.py 用于根据词法规则生成词法分析器lexer.py
2. generate_parser.py 用于根据语法规则生成语法分析器parser.py
3. compiler.py根据生成的lexer.py和parser.py生成编译器执行test.code
4. 运行项目时执行run.sh
