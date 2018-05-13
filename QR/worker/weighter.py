#!/usr/bin/python
# -*- coding: UTF-8 -*-

import pynlpir
import tool
import codecs
import numpy as np
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.models import LdaModel
from gensim import corpora


def ie():
    """
    信息熵权重
    :return:
    """
    # 获取查询
    db_tool = tool.DBtool()
    queries = db_tool.select_queries()
    segmented_queries = db_tool.select_segmented_queries()
    # 获取权重
    pynlpir.open()
    temp = {}
    for query in queries:
        temp[query['query_id']] = pynlpir.get_key_words(query['query'], weighted=True, max_words=100)
    pynlpir.close()
    # 组成字符串
    for query in segmented_queries:
        weight = temp[query['query_id']]
        dic = {}
        min_w = 2.0
        for w in weight:
            dic[w[0].encode('utf-8')] = w[1]
            if w[1] < min:
                min_w = w[1]

        words = query['segmented_query'].strip().split(' ')
        weight = []
        for word in words:
            if word in dic:
                weight.append(dic[word])
            else:
                weight.append(min_w / 2)
        s = sum(weight)
        weight = ['%.5f' % (x / s) for x in weight]
        # 更新数据库
        db_tool.update_weight(query['query_id'], ' '.join(weight), 'weight_ie')
    db_tool.close()


def tf_idf(idf_path='F:/Data/Chinese/idf'):
    """
    tf_idf权重
    :return:
    """    """
    信息熵权重
    :return:
    """
    # 载入idf
    dic = {}
    with codecs.open(idf_path, 'r', 'utf-8') as f:
        for line in f:
            word = line.strip().split('\t')
            dic[word[0].encode('utf-8')] = float(word[1])
    # 获取查询
    db_tool = tool.DBtool()
    segmented_queries = db_tool.select_segmented_queries()
    # 获取权重
    # 组成字符串
    for query in segmented_queries:
        words = query['segmented_query'].strip().split(' ')
        weight = []
        for word in words:
            weight.append(dic[word])
        s = sum(weight)
        weight = ['%.5f' % (x / s) for x in weight]
        # 更新数据库
        db_tool.update_weight(query['query_id'], ' '.join(weight), 'weight_tf_idf')
    db_tool.close()


def topic(lda_path='F:/Data/Chinese/LDA/30/lda70.model', dictionary_path='dic.dictionary'):
    """
    主题模型权重
    :param lda_path: lda模型路径
    :param dictionary_path 词典路径
    :return:
    """
    # 载入模型，载入词典
    lda = LdaModel.load(lda_path)
    dic = corpora.Dictionary.load(dictionary_path)
    matrix = lda.get_topics()  # topic_num * word_num
    # 获取查询
    db_tool = tool.DBtool()
    segmented_queries = db_tool.select_segmented_queries()
    # 获取权重
    # 组成字符串
    for query in segmented_queries:
        words = query['segmented_query'].strip().split(' ')
        doc_bow = dic.doc2bow(words)  # 文档转换成bow
        doc_topics = lda.get_document_topics(doc_bow, minimum_probability=0.00000001)  # 得到新文档的主题分布
        weight_topics = np.array([x[1] for x in doc_topics])
        assert len(weight_topics) == np.shape(matrix)[0]
        weight = []
        for word in words:
            word_id = dic.doc2bow([word])[0][0]
            temp = matrix[:, word_id]
            # temp = np.multiply(weight_topics, np.log(temp))
            temp = np.multiply(weight_topics, np.multiply(temp, np.log(temp)))
            # temp = np.log(np.multiply(weight_topics, temp))
            # temp = np.log(np.sum(np.multiply(weight_topics, temp)))
            weight.append(np.sum(temp))
        s = sum(weight)
        weight = ['%.5f' % (x / s) for x in weight]
        if len(weight) == 0:
            print query['query_id']
        # 更新数据库
        db_tool.update_weight(query['query_id'], ' '.join(weight), 'weight_topic')
        # print ' '.join(weight)


if __name__ == '__main__':
    '''
    信息熵
    '''
    # ie()

    '''
    tf-idf
    '''
    # tf_idf()

    '''
    lda
    '''
    topic()
