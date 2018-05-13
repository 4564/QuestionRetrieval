#!/usr/bin/env python
# -*- encoding:UTF-8 -*-

import os
import json
import codecs
import pynlpir
import math


def segment(path='F:/Data/Chinese/chinese.json', json_path='F:/Data/Chinese/chinese_token.json'):
    """
    NLPIR分词+根据词性清洗+去掉为问题或回答空的项
    :param path: 源数据路径
    :param json_path: 结果保存路径
    :return:
    """
    # 启动分词工具
    pynlpir.open()
    # 只保留文本部分，并分词，根据词性过滤
    # 保留以下词性的词，并去除词性标记
    # 词性含义请查看https://github.com/tsroten/pynlpir/blob/master/pynlpir/pos_map.py
    word_filter = {'noun', 'time word', 'locative word', 'noun of locality', 'verb',
                   'adjective', 'distinguishing word', 'status word', 'numeral'}
    # 清除分词异常的数据
    question_id_filter = {294118450, 300106271, 291834409}

    # 边读边处理边写入文件，减少内存消耗
    count = 0
    with open(path, 'r') as f_in, open(json_path, 'w') as f_out:
        for line in f_in:
            q = json.loads(line)
            if q['question_id'] in question_id_filter:
                continue
            # 干掉有换行的情况 小写化
            if '\n' in q['question']:
                print 'question:'
                print q['question']
                q['question'] = q['question'].replace('\n', ' ')
            q['question'] = [w[0] for w in pynlpir.segment(q['question'].lower()) if
                             w[1] in word_filter and w[0] != u'']

            for a in q['answers']:
                # 干掉有换行的情况
                if '\n' in a['answer']:
                    print 'answer:'
                    print a['answer']
                    a['answer'] = a['answer'].replace('\n', ' ')
                a['answer'] = [w[0] for w in pynlpir.segment(a['answer'].lower()) if
                               w[1] in word_filter and w[0] != u'']
            # 清除回答为空
            q['answers'] = [a for a in q['answers'] if len(a['answer']) > 0]
            count = count + 1
            if count % 1000 == 0:
                print count
            # 清除回答列表为空和问题为空的
            if len(q['question']) > 0 and len(q['answers']) > 0:
                f_out.write(json.dumps(q))
                f_out.write('\n')
    pynlpir.close()


def extract_dic(path='F:/Data/Chinese/chinese_token.json', dic_path='F:/Data/Chinese/dic'):
    """
    统计单词获取词典
    :param path:
    :param dic_path:
    :return:
    """
    print '统计词频:'
    print path
    dic = {}
    with open(path, 'r') as f:
        for line in f:
            q = json.loads(line)
            for w in q['question']:
                if w in dic:
                    dic[w] = dic[w] + 1
                else:
                    dic[w] = 1
            for a in q['answers']:
                for w in a['answer']:
                    if w in dic:
                        dic[w] = dic[w] + 1
                    else:
                        dic[w] = 1

    with codecs.open(dic_path, 'w', 'utf-8') as f:
        word_list = sorted(dic.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)
        for w in word_list:
            f.write(w[0])
            f.write('\t%d\n' % w[1])
    print '保存词典:'
    print dic_path


def extract_idf(path='F:/Data/Chinese/chinese_token.json',
                dic_path='F:/Data/Chinese/dic',
                min_tf=5,
                idf_path='F:/Data/Chinese/idf'):
    """
    提取词的idf
    :param path: 源数据路径
    :param dic_path: 词典路径
    :param min_tf: 最小词频
    :param idf_path: idf保存路径
    :return:
    """
    print '读取词典:'
    print dic_path
    dic = {}
    with codecs.open(dic_path, 'r', 'utf-8') as f:
        for line in f:
            temp = line.strip().split('\t')
            if len(temp) == 2:
                dic[temp[0]] = int(temp[1])
    # 从词典清除低频词
    start = len(dic)
    temp = {}
    for w in dic:
        if dic[w] >= min_tf:
            temp[w] = 0
    dic = temp
    print '清理低频词%d->%d' % (start, len(dic))
    # 边读边处理边写入文件，减少内存消耗
    print '清理数据'
    print path
    with open(path, 'r') as f_in, \
            codecs.open(idf_path, 'w', 'utf-8') as f_idf:
        length_doc = 0
        for line in f_in:
            q = json.loads(line)
            # 依据词典，过滤词汇，然后清除问题为空的、回答为空的、回答过长的和回答列表为空的
            q['question'] = [w for w in q['question'] if w in dic]
            for a in q['answers']:
                a['answer'] = [w for w in a['answer'] if w in dic]
            # 清除回答
            q['answers'] = [a for a in q['answers'] if 0 < len(a['answer'])]
            # 清理问题
            if len(q['question']) > 0 or len(q['answers']) > 0:
                length_doc = length_doc + 1
                temp = set(q['question'])
                for a in q['answers']:
                    temp = temp.union(set(a['answer']))
                for w in temp:
                    dic[w] = dic[w] + 1
        length_doc = float(length_doc)
        for w in dic:
            dic[w] = math.log(length_doc / dic[w])
        word_list = sorted(dic.items(), lambda x, y: cmp(x[1], y[1]), reverse=False)
        for w in word_list:
            f_idf.write(w[0])
            f_idf.write('\t%.8f\n' % w[1])
    print '保存词典:'
    print idf_path
    print length_doc


def extract_parallel_corpora(path='F:/Data/Chinese/chinese_token.json',
                             dic_path='F:/Data/Chinese/dic',
                             min_tf=5,
                             corpus_path='F:/Data/Chinese'):
    """
    从已分好词的数据中抽取出平行语料，根据词典做过滤低频词
    为了抑制翻译噪声，这里限制了回答最大长度
    :param path: 源数据路径
    :param dic_path: 词典路径
    :param min_tf: 最小词频
    :param corpus_path: 语料保存路径
    :return:
    """
    print '读取词典:'
    print dic_path
    dic = {}
    with codecs.open(dic_path, 'r', 'utf-8') as f:
        for line in f:
            temp = line.strip().split('\t')
            if len(temp) == 2:
                dic[temp[0]] = int(temp[1])
    # 从词典清除低频词
    start = len(dic)
    temp = set()
    for w in dic:
        if dic[w] >= min_tf:
            temp.add(w)
    dic = temp
    print '清理低频词%d->%d' % (start, len(dic))

    # 边读边处理边写入文件，减少内存消耗
    print '清理数据'
    print path
    with open(path, 'r') as f_in, \
            codecs.open(os.path.join(corpus_path, 'S'), 'w', 'utf-8') as f_s, \
            codecs.open(os.path.join(corpus_path, 'T'), 'w', 'utf-8') as f_t:
        for line in f_in:
            q = json.loads(line)
            # 依据词典，过滤词汇，然后清除问题为空的、回答为空的、回答过长的和回答列表为空的
            q['question'] = [w for w in q['question'] if w in dic]
            for a in q['answers']:
                a['answer'] = [w for w in a['answer'] if w in dic]
            # 清除回答
            q['answers'] = [a for a in q['answers'] if 0 < len(a['answer']) < 100]
            # 清理问题
            if len(q['question']) > 0 and len(q['answers']) > 0:
                for a in q['answers']:
                    f_s.write(' '.join(q['question']))
                    f_s.write('\n')
                    f_t.write(' '.join(a['answer']))
                    f_t.write('\n')
                    f_s.write(' '.join(a['answer']))
                    f_s.write('\n')
                    f_t.write(' '.join(q['question']))
                    f_t.write('\n')


def extract_topic_corpora(path='F:/Data/Chinese/chinese_token.json',
                          dic_path='F:/Data/Chinese/dic',
                          min_tf=5,
                          corpus_path='F:/Data/Chinese/topic'):
    """
    从已分好词的数据中抽取出主题模型语料，根据词典做过滤低频词
    同时为了增加文档长度，把问题和其所有回答进行了连接
    :param path: 源数据路径
    :param dic_path: 词典路径
    :param min_tf: 最小词频
    :param corpus_path: 语料保存路径
    :return:
    """
    print '读取词典:'
    print dic_path
    dic = {}
    with codecs.open(dic_path, 'r', 'utf-8') as f:
        for line in f:
            temp = line.strip().split('\t')
            if len(temp) == 2:
                dic[temp[0]] = int(temp[1])
    # 从词典清除低频词
    start = len(dic)
    temp = set()
    for w in dic:
        if dic[w] >= min_tf:
            temp.add(w)
    dic = temp
    print '清理低频词%d->%d' % (start, len(dic))

    # 边读边处理边写入文件，减少内存消耗
    print '清理数据'
    print path
    with open(path, 'r') as f_in, codecs.open(corpus_path, 'w', 'utf-8') as f_out:
        for line in f_in:
            q = json.loads(line)
            # 依据词典，过滤词汇，然后清除问题为空的、回答为空的和回答列表为空的
            q['question'] = [w for w in q['question'] if w in dic]
            for a in q['answers']:
                a['answer'] = [w for w in a['answer'] if w in dic]
            # 清除回答
            q['answers'] = [a for a in q['answers'] if len(a['answer']) > 0]
            # 清理问题
            if len(q['question']) > 0 and len(q['answers']) > 0:
                f_out.write(' '.join(q['question']))
                f_out.write(' ')
                f_out.write(' '.join([' '.join(a['answer']) for a in q['answers']]))
                f_out.write('\n')


if __name__ == '__main__':
    """
    将融合后的数据进行分词，同时整理数据
    """
    # segment()  # 'test_data.json'

    """
    从分词数据抽取词典，带词频
    """
    # extract_dic()

    """
    从分词数据抽取idf
    """
    # extract_idf()

    """
    从分词数据抽取平行语料
    """
    # extract_parallel_corpora()  # 'test_data.json'

    """
    从分词数据抽取主题模型语料
    """
    # extract_topic_corpora()  # 'test_data.json'
