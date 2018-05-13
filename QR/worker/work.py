#!/usr/bin/python
# -*- encoding: UTF-8 -*-

import tool
from worker.ranker import LM
from worker.ranker import TLM
from worker.ranker import T2LM
from worker.ranker import IT2LM
from worker.ranker import WIT2LM

import pynlpir
import codecs
import time
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.models import LdaModel
from gensim import corpora


def load_translation(translation_path='F:/Data/Chinese/Translation/S2T.actual.ti.final'):
    """
    载入翻译概率
    :param translation_path: 翻译概率文件
    :return: 翻译词典
    """
    dictionary = {}
    with codecs.open(translation_path, 'r', 'utf-8') as f:
        for line in f:
            word_pair = line.strip().split(' ')
            assert len(word_pair) == 3
            if word_pair[0] != 'NULL' and word_pair[1] != 'NULL' and word_pair[0] != '' and word_pair[1] != '':
                if word_pair[0] in dictionary:
                    dictionary[word_pair[0]][word_pair[1]] = float(word_pair[2])
                else:
                    dictionary[word_pair[0]] = {word_pair[1]: float(word_pair[2])}
    return dictionary


def load_background_probability(dictionary_path='F:/Data/Chinese/dic', min_tf=5):
    """
    载入背景分布概率
    :param dictionary_path: 词典位置
    :param min_tf: 最低词频
    :return: 背景分布词典
    """
    dictionary = {}
    with codecs.open(dictionary_path, 'r', 'utf-8') as f:
        for line in f:
            word = line.strip().split('\t')
            if len(word) == 2 and int(word[1]) >= min_tf:
                dictionary[word[0]] = int(word[1])
    sum_count = float(sum(dictionary.values()))
    for word in dictionary:
        dictionary[word] = dictionary[word] / sum_count
    return dictionary


if __name__ == '__main__':
    """
    载入背景分布
    """
    start = time.time()
    background_dic = load_background_probability()
    print '载入背景分布耗时%ds' % (time.time() - start)
    start = time.time()
    """
    载入翻译概率
    """
    start = time.time()
    translation_dic = load_translation()
    print '载入翻译概率耗时%ds' % (time.time() - start)
    start = time.time()
    """
    载入词项过滤器
    """
    word_filter = tool.WordFilter()
    """
    载入模型，载入词典
    """
    lda = LdaModel.load('F:/Data/Chinese/LDA/30/lda70.model')
    id2word_dic = corpora.Dictionary.load('dic.dictionary')

    """
    载入测试数据，包括查询和候选，进行分词和过滤
    保存结果
    """
    f_outs = [# open('F:/Data/Chinese/Result/t2lm1.tsv', 'w'),
              # open('F:/Data/Chinese/Result/it2lm1.tsv', 'w'),
              # open('F:/Data/Chinese/Result/it2lm2.tsv', 'w'),
              # open('F:/Data/Chinese/Result/it2lm3.tsv', 'w'),
              # open('F:/Data/Chinese/Result/it2lm4.tsv', 'w'),
              # open('F:/Data/Chinese/Result/it2lm5.tsv', 'w'),
              # open('F:/Data/Chinese/Result/it2lm6.tsv', 'w'),
              # open('F:/Data/Chinese/Result/wit2lm1.tsv', 'w'),
              # open('F:/Data/Chinese/Result/wit2lm2.tsv', 'w'),
              # open('F:/Data/Chinese/Result/wit2lm3.tsv', 'w'),
              # open('F:/Data/Chinese/Result/wit2lm4.tsv', 'w'),
              # open('F:/Data/Chinese/Result/wit2lm5.tsv', 'w'),
              # open('F:/Data/Chinese/Result/wit2lm6.tsv', 'w'),
                open('F:/Data/Chinese/Result/wit2lm_tf_idf.tsv', 'w'),
                open('F:/Data/Chinese/Result/wit2lm_ie.tsv', 'w')]
    rankers = [# T2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 0.3, 'mu2': 0.1, 'mu3': 0.4, 'mu4': 0.2}),
               # IT2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 0.3, 'mu2': 0.1, 'mu3': 0.4, 'mu4': 0.2}),
               # IT2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 0.4, 'mu2': 0.1, 'mu3': 0.3, 'mu4': 0.2}),
               # IT2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 0.5, 'mu2': 0.1, 'mu3': 0.2, 'mu4': 0.2}),
               # IT2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 0.2, 'mu2': 0.2, 'mu3': 0.4, 'mu4': 0.2}),
               # IT2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 0.4, 'mu2': 0.2, 'mu3': 0.2, 'mu4': 0.2}),
               # IT2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 0.1, 'mu2': 0.2, 'mu3': 0.5, 'mu4': 0.2}),
               # WIT2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 0.3, 'mu2': 0.1, 'mu3': 0.4, 'mu4': 0.2}),
               # WIT2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 0.4, 'mu2': 0.1, 'mu3': 0.3, 'mu4': 0.2}),
               # WIT2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 0.5, 'mu2': 0.1, 'mu3': 0.2, 'mu4': 0.2}),
               # WIT2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 0.2, 'mu2': 0.2, 'mu3': 0.4, 'mu4': 0.2}),
               # WIT2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 0.4, 'mu2': 0.2, 'mu3': 0.2, 'mu4': 0.2}),
               # WIT2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 0.1, 'mu2': 0.2, 'mu3': 0.5, 'mu4': 0.2}),
                WIT2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 0.3, 'mu2': 0.1, 'mu3': 0.4, 'mu4': 0.2})]
                # LM(background_dic),
                # TLM(background_dic, translation_dic, {'alpha': 1.0, 'beta': 0, 'gamma': 0}),
                # T2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 1.0, 'mu2': 0, 'mu3': 0, 'mu4': 0}),
                # WIT2LM(background_dic, translation_dic, lda, id2word_dic, {'mu1': 1.0, 'mu2': 0, 'mu3': 0, 'mu4': 0})
    pynlpir.open()
    dbTool = tool.DBtool()
    queries = dbTool.select_segmented_queries_weight()
    # queries = [{'query_id': 1014455L,
    #             'query':
    #                 ['古代', '小说', '用', '沉鱼落雁', '闭月羞花', '形容', '女性', '美', '闭', '月', '是', '指'],
    #             'weight':
    #                 [0.08123, 0.08134, 0.03914, 0.15939, 0.16197, 0.09668, 0.08489, 0.06728, 0.10086, 0.05610, 0.00975, 0.06138]}]
    for query in queries:
        # query变成Unicode
        query['query'] = [x.decode('utf-8') for x in query['query']]
        # query['weight'] = query['weight_topic']
        candidates = dbTool.select_candidates(query['query_id'])
        # 候选分词
        # start = time.time()
        for candidate in candidates:
            candidate['question'] = word_filter.filter(pynlpir.segment(candidate['question']))
            candidate['answers'] = [word_filter.filter(pynlpir.segment(x)) for x in candidate['answers']]
        # print '分词耗时%ds' % (time.time() - start)
        # for i in range(len(rankers)):
        #     # 检索
        #     start = time.time()
        #     res = rankers[i].rank(query, candidates)[0:10]
        #     print '检索耗时%ds' % (time.time() - start)
        #     # 写入文件
        #     f_outs[i].write('%d\t%s\n' % (query['query_id'], '\t'.join([str(x[0]) for x in res])))
        query['weight'] = query['weight_tf_idf']
        res = rankers[0].rank(query, candidates)[0:10]
        f_outs[0].write('%d\t%s\n' % (query['query_id'], '\t'.join([str(x[0]) for x in res])))
        query['weight'] = query['weight_ie']
        res = rankers[0].rank(query, candidates)[0:10]
        f_outs[1].write('%d\t%s\n' % (query['query_id'], '\t'.join([str(x[0]) for x in res])))
        print query['query_id']
    pynlpir.close()
    for x in f_outs:
        x.close()
