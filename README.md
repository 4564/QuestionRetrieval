# QuestionRetrieval
# 实验要用到的工具
分词 https://github.com/tsroten/pynlpir 注意https://github.com/tsroten/pynlpir/issues/101
翻译模型 giza++https://github.com/moses-smt/giza-pp 或者多线程版本mgiza https://github.com/moses-smt/mgiza
注意翻译模型建议在Linux下运行其中mgiza需要boost库
主题模型 gensim https://github.com/RaRe-Technologies/gensim 安装 pip install -U gensim

# 实验代码部分 
QR部分为Python代码，其中data_process为数据处理部分，包括分词，处理成训练预料，导入数据库等；worker为实验代码
web部分为网页方便人工标记数据
database为数据表结构
