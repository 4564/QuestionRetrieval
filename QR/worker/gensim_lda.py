# coding=utf-8
import codecs
import time
import tool.WordFilter
import pynlpir
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim import corpora
from gensim.models import LdaModel
from gensim.models import LdaMulticore


def load_corpus(corpus_path):
    """
    载入语料
    :param corpus_path: 语料路径
    :return: 多维数组
    """
    start = time.time()
    data = []
    print '读取语料：'
    print corpus_path
    with codecs.open(corpus_path, 'r', 'utf-8') as f:
        for line in f:
            words = line.strip().split(' ')
            data.append(words)
    print '语料长度为：%d' % len(data)
    print '读取完成，耗时%ds' % (time.time() - start)
    return data


def create_dictionary(data, dictionary_path):
    """
    生成词典
    :param data:多维数组的分词好的语料
    :param dictionary_path: 词典数据保存位置
    :return: 词典
    """
    start = time.time()
    dictionary = corpora.Dictionary(data)
    print '词典生成完成，耗时%ds' % (time.time() - start)
    # 保存字典
    dictionary.save(dictionary_path)
    return dictionary


def create_bow_corpus(data, dictionary):
    """
    语料bow化
    :param data: 分词好的语料
    :param dictionary: 词典
    :return: bow化语料
    """
    start = time.time()
    bow_corpus = [dictionary.doc2bow(text) for text in data]
    print 'doc2bow完成，耗时%ds' % (time.time() - start)
    return bow_corpus


def train_lda(corpus_bow, dictionary, topic_num, model_path):
    """
    训练lda模型，保存到指定位置
    :param corpus_bow: 语料
    :param dictionary: 词典
    :param topic_num: 主题数
    :param model_path: 模型保存位置
    :return:
    """
    start = time.time()
    print '开始训练: %d个主题' % topic_num
    model_lda = LdaModel(corpus=corpus_bow, id2word=dictionary, num_topics=topic_num,
                         alpha='asymmetric', minimum_probability=0.0001, minimum_phi_value=0.00001, passes=4)
    print '训练耗时%ds' % (time.time() - start)
    # 保存模型
    model_lda.save(model_path)


def train_lda_multicore(corpus_bow, dictionary, topic_num, model_path):
    """
    多核训练
    :param corpus_bow: 语料
    :param dictionary: 词典
    :param topic_num: 主题数
    :param model_path: 模型保存位置
    :return:
    """
    start = time.time()
    print '开始训练: %d个主题' % topic_num
    model_lda = LdaMulticore(corpus=corpus_bow, id2word=dictionary, num_topics=topic_num,
                             alpha='asymmetric', minimum_probability=0.0001, minimum_phi_value=0.00001, passes=4,
                             workers=2)
    print '多线程训练耗时%ds' % (time.time() - start)
    # 保存模型
    model_lda.save(model_path)


def updte_lda(corpus_path, dictionary_path, model_path, iter_num):
    """
    载入模型，迭代训练，覆盖原文件保存
    :param corpus_path: 语料路径
    :param dictionary_path: 词典路径
    :param model_path: 模型路径
    :param iter_num: 迭代次数
    :return:
    """
    dictionary = load_dictionary(dictionary_path)
    corpus_bow = create_bow_corpus(load_corpus(corpus_path), dictionary)
    model_lda = load_model(model_path)
    start = time.time()
    model_lda.update(corpus_bow, passes=iter_num)
    # 保存模型
    model_lda.save(model_path)


def load_dictionary(dictionary_path):
    """
    载入字典
    :param dictionary_path: 字典文件路径
    :return: 字典
    """
    print '载入字典'
    print dictionary_path
    dictionary = corpora.Dictionary.load(dictionary_path)
    return dictionary


def load_model(model_path):
    """
    载入模型
    :param model_path:模型文件路径
    :return: 模型
    """
    print '载入模型:'
    print model_path
    start = time.time()
    lda = LdaModel.load(model_path)
    print '耗时%ds' % (time.time() - start)
    return lda


def get_topics(doc, dictionary, lda):
    """
    获取文档的主题分布
    :param doc: 已分好词的文档
    :param dictionary: 字典
    :param lda: lda模型
    :return: 主题分布
    """
    doc_bow = dictionary.doc2bow(doc)  # 文档转换成bow
    doc_lda = lda[doc_bow]  # 得到新文档的主题分布
    return doc_lda


if __name__ == '__main__':
    # path_corpus = 'test_topic.txt'
    path_dictionary = 'dic.dictionary'
    path_model = 'F:/Data/Chinese/LDA/20/lda70.model'
    new_doc = '大学哪个专业就业比较好？'
    word_filter = tool.WordFilter()
    pynlpir.open()
    words = pynlpir.segment(new_doc.lower())
    pynlpir.close()
    print words
    words = word_filter.filter(words)
    print words

    """
    训练lda模型并保存
    """
    # train_data = load_corpus(path_corpus)
    # dic = create_dictionary(train_data, path_dictionary)
    # bow_corpus = create_bow_corpus(train_data, dic)
    # for i in range(10, 100, 20):
    #     train_lda(bow_corpus, dic, i, 'lda%d.model' % i)
    #     train_lda_multicore(bow_corpus, dic, i, 'ldam%d.model' % i)

    """
    更新模型
    """
    # updte_lda('test_topic.txt', 'test_dic.dictionary', 'test_lda.model', 2)

    """
    载入词典
    """
    dic = load_dictionary(path_dictionary)

    """
    载入模型
    """
    lda_model = load_model(path_model)

    """
    获取新文档的主题分布
    """
    lda_doc = get_topics(words, dic, lda_model)

    # 输出新文档的主题分布
    print lda_doc
    for topic in lda_doc:
        print "%f\t%s" % (topic[1], lda_model.print_topic(topic[0]))

# topic_list = lda.print_topics(20)
# print type(lda.print_topics(20))
# print len(lda.print_topics(20))
#
# for topic in topic_list:
#     print topic
# print lda.print_topic(1)
