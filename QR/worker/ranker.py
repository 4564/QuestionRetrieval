#!/usr/bin/python
# -*- encoding: UTF-8 -*-

import math
import numpy as np
from collections import Counter


class Ranker:
    def __init__(self):
        print '父类初始化'

    def rank(self, query, candidates):
        """
        排序，这里候选问答对使用树状结构
        :param query: 查询 {'query':['word1', 'word2',...]} Unicode
        :param candidates: 候选问题，带多个回答，带ID
        [{'question': ['word', ...], 'question_id': id, 'answers': [['word2',...], ...]}, ...] Unicode
        :return: 排序好的候选列表
        """
        print '排序'

    def __similarity(self, query, candidate):
        """
        计算相似度，LM中不考虑回答，对求积取对数
        :param query: 查询 [word1, word2,...] Unicode
        :param candidate: 候选问题，带多个回答
        {'question': ['word', ...], 'question_id': id, 'answers': [['word2',...], ...]} Unicode
        :return: 相似度
        """
        print '相关度计算'


class LM(Ranker):
    def __init__(self, background_dictionary):
        self.background_dic = background_dictionary  # Unicode

    def rank(self, query, candidates):
        """
        排序，这里候选问答对使用树状结构
        :param query: 查询 {'query':['word1', 'word2',...]} Unicode
        :param candidates: 候选问题，带多个回答，带ID
        [{'question': ['word', ...], 'question_id': id, 'answers': [['word2',...], ...]}, ...] Unicode
        :return: 排序好的候选列表
        """
        sims = {}
        for candidate in candidates:
            sim = self.__similarity(query['query'], candidate)
            sims[candidate['question_id']] = sim
        return sorted(sims.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)

    def __similarity(self, query, candidate):
        """
        计算相似度，LM中不考虑回答，对求积取对数
        :param query: 查询 [word1, word2,...] Unicode
        :param candidate: 候选问题，带多个回答
        {'question': ['word', ...], 'question_id': id, 'answers': [['word2',...], ...]} Unicode
        :return: 相似度
        """
        sim = 0
        length = len(candidate['question'])
        lam = 1.0 / (length + 1)
        question = Counter(candidate['question'])
        for word in query:
            temp = self.background_dic[word] * lam
            if word in question:
                temp = temp + (1 - lam) * question[word] / length
            sim = sim + math.log(temp)
        return sim


class TLM(Ranker):
    def __init__(self, background_dictionary, translation_dictionary, parameters):
        self.background_dic = background_dictionary  # Unicode
        self.translation_dic = translation_dictionary
        self.parameters = parameters

    def rank(self, query, candidates):
        """
        排序，这里候选问答对使用树状结构
        :param query: 查询 {'query':['word1', 'word2',...]} Unicode
        :param candidates: 候选问题，带多个回答，带ID
        [{'question': ['word', ...], 'question_id': id, 'answers': [['word2',...], ...]}, ...] Unicode
        :return: 排序好的候选列表
        """
        sims = {}
        for candidate in candidates:
            sim = self.__similarity(query['query'], candidate)
            sims[candidate['question_id']] = sim
        return sorted(sims.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)

    def __similarity(self, query, candidate):
        """
        计算相似度，对求积取对数
        :param query: 查询 [word1, word2,...] Unicode
        :param candidate: 候选问题，带多个回答
        {'question': ['word', ...], 'question_id': id, 'answers': [['word2',...], ...]} Unicode
        :return: 相似度
        """
        sim = -9999999.9
        length_q = len(candidate['question'])
        lam = 1.0 / (length_q + 1)
        question = Counter(candidate['question'])
        for answer in candidate['answers']:
            temp = 0
            length_a = len(answer)
            answer = Counter(answer)
            for word in query:
                temp_w = 0
                if word in question and length_q != 0:
                    temp_w = self.parameters['alpha'] * question[word] / length_q
                if self.translation_dic is not None and word in self.translation_dic and length_q != 0:
                    temp_t = 0
                    for x in question:
                        if x in self.translation_dic[word]:
                            temp_t = temp_t + self.translation_dic[word][x] * question[x]
                    temp_w = temp_w + self.parameters['beta'] * temp_t / length_q
                if word in answer and length_a != 0:
                    temp_w = temp_w + self.parameters['gamma'] * answer[word] / length_a
                temp = temp + math.log(temp_w * (1 - lam) + self.background_dic[word] * lam)

            if temp > sim:
                sim = temp
        return sim


class T2LM(Ranker):
    def __init__(self, background_dictionary, translation_dictionary, lda_model, id2word_dictionary, parameters):
        """
        :param background_dictionary: 背景词典 Unicode
        :param translation_dictionary: 翻译词典
        :param lda_model: LDA模型
        :param id2word_dictionary: 词袋化词典
        :param parameters: 参数
        """
        self.background_dic = background_dictionary
        self.translation_dic = translation_dictionary
        self.matrix = lda_model.get_topics()
        self.id2word_dic = id2word_dictionary
        self.parameters = parameters

    def rank(self, query, candidates):
        """
        排序，这里候选问答对使用树状结构
        :param query: 查询 {'query':['word1', 'word2',...]} Unicode
        :param candidates: 候选问题，带多个回答，带ID
        [{'question': ['word', ...], 'question_id': id, 'answers': [['word2',...], ...]}, ...] Unicode
        :return: 排序好的候选列表
        """
        sims = {}
        for candidate in candidates:
            sims[candidate['question_id']] = self.__similarity(query['query'], candidate)
        return sorted(sims.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)

    def __similarity(self, query, candidate):
        """
        计算相似度，对求积取对数
        :param query: 查询 [word1, word2,...] Unicode
        :param candidate: 候选问题，带多个回答
        {'question': ['word', ...], 'question_id': id, 'answers': [['word2',...], ...]} Unicode
        :return: 相似度
        """
        sim = -9999999.9
        length_q = len(candidate['question'])
        lam = 1.0 / (length_q + 1)
        question = Counter(candidate['question'])
        for answer in candidate['answers']:
            temp = 0
            for word in query:
                temp_w = 0
                if word in question and length_q != 0:
                    temp_w = self.parameters['mu1'] * question[word] / length_q
                if self.translation_dic is not None and word in self.translation_dic and length_q != 0:
                    temp_t = 0
                    for x in question:
                        if x in self.translation_dic[word]:
                            temp_t = temp_t + self.translation_dic[word][x] * question[x]
                    temp_w = temp_w + self.parameters['mu2'] * temp_t / length_q
                if word in self.id2word_dic.token2id and length_q != 0:  # word在id2word_dic中
                    word_topics = self.matrix[:, self.id2word_dic.token2id[word]]
                    question_bow = self.id2word_dic.doc2bow(candidate['question'])
                    if len(question_bow) > 0:
                        question_matrix = self.matrix[:, [x[0] for x in question_bow]].T
                        question_cnt = np.array([x[1] for x in question_bow])
                        temp_t = np.sum(np.multiply(question_matrix.dot(word_topics), question_cnt))
                        temp_w = temp_w + self.parameters['mu3'] * temp_t / length_q
                length_a = len(answer)
                answer = Counter(answer)
                if length_a != 0 and word in answer:
                    temp_w = temp_w + self.parameters['mu4'] * answer[word] / length_a
                temp = temp + math.log(temp_w * (1 - lam) + self.background_dic[word] * lam)
            if temp > sim:
                sim = temp
        return sim


class IT2LM(Ranker):
    def __init__(self, background_dictionary, translation_dictionary, lda_model, id2word_dictionary, parameters):
        """
        :param background_dictionary: 背景词典 Unicode
        :param translation_dictionary: 翻译词典
        :param lda_model: LDA模型
        :param id2word_dictionary: 词袋化词典
        :param parameters: 参数
        """
        self.background_dic = background_dictionary
        self.translation_dic = translation_dictionary
        self.lda = lda_model
        self.matrix = self.lda.get_topics()
        self.id2word_dic = id2word_dictionary
        self.parameters = parameters

    def rank(self, query, candidates):
        """
        排序，这里候选问答对使用树状结构
        :param query: 查询 {'query':['word1', 'word2',...]}
        :param candidates: 候选问题，带多个回答，带ID
        [{'question': ['word', ...], 'question_id': id, 'answers': [['word2',...], ...]}, ...]
        :return: 排序好的候选列表
        """
        sims = {}
        doc_bow = self.id2word_dic.doc2bow(query['query'])  # 文档转换成bow
        doc_topics = self.lda.get_document_topics(doc_bow, minimum_probability=0.00000001)  # 得到新文档的主题分布
        weight = np.array([x[1] for x in doc_topics])
        for candidate in candidates:
            sims[candidate['question_id']] = self.__similarity(query['query'], weight, candidate)
        return sorted(sims.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)

    def __similarity(self, query, weight, candidate):
        """
        计算相似度，LM中不考虑回答，对求积取对数
        :param query: 查询 [word1, word2,...] Unicode
        :param weight: 主题权重
        :param candidate: 候选问题，带多个回答
        {'question': ['word', ...], 'question_id': id, 'answers': [['word2',...], ...]} Unicode
        :return: 相似度
        """
        sim = -9999999.9
        length_q = len(candidate['question'])
        lam = 1.0 / (length_q + 1)
        question = Counter(candidate['question'])
        for answer in candidate['answers']:
            temp = 0
            for word in query:
                temp_w = 0
                if word in question and length_q != 0:
                    temp_w = self.parameters['mu1'] * question[word] / length_q
                if self.translation_dic is not None and word in self.translation_dic:
                    temp_t = 0
                    for x in question:
                        if x in self.translation_dic[word]:
                            temp_t = temp_t + self.translation_dic[word][x] * question[x]
                    if length_q != 0:
                        temp_w = temp_w + self.parameters['mu2'] * temp_t / length_q
                if word in self.id2word_dic.token2id and length_q != 0:  # word在id2word_dic中
                    word_topics = np.multiply(weight, self.matrix[:, self.id2word_dic.token2id[word]])
                    question_bow = self.id2word_dic.doc2bow(candidate['question'])
                    if len(question_bow) > 0:
                        question_matrix = self.matrix[:, [x[0] for x in question_bow]].T
                        question_cnt = np.array([x[1] for x in question_bow])
                        temp_t = np.sum(np.multiply(question_matrix.dot(word_topics), question_cnt))
                        temp_w = temp_w + self.parameters['mu3'] * temp_t / length_q
                length_a = len(answer)
                answer = Counter(answer)
                if word in answer and length_a != 0:
                    temp_w = temp_w + self.parameters['mu4'] * answer[word] / length_a
                temp = temp + math.log(temp_w * (1 - lam) + self.background_dic[word] * lam)
            if temp > sim:
                sim = temp
        return sim


class WIT2LM(Ranker):
    def __init__(self, background_dictionary, translation_dictionary, lda_model, id2word_dictionary, parameters):
        """
        :param background_dictionary: 背景词典 Unicode
        :param translation_dictionary: 翻译词典
        :param lda_model: LDA模型
        :param id2word_dictionary: 词袋化词典
        :param parameters: 参数
        """
        self.background_dic = background_dictionary
        self.translation_dic = translation_dictionary
        self.lda = lda_model
        self.matrix = self.lda.get_topics()
        self.id2word_dic = id2word_dictionary
        self.parameters = parameters

    def rank(self, query, candidates):
        """
        排序，这里候选问答对使用树状结构
        :param query: 查询 {'query':['word1', 'word2',...], 'weight_word': [w1, w2,...]} Unicode
        :param candidates: 候选问题，带多个回答，带ID
        [{'question': ['word', ...], 'question_id': id, 'answers': [['word2',...], ...]}, ...] Unicode
        :return: 排序好的候选列表
        """
        sims = {}
        doc_bow = self.id2word_dic.doc2bow(query)  # 文档转换成bow
        doc_topics = self.lda.get_document_topics(doc_bow, minimum_probability=0.00000001)  # 得到新文档的主题分布
        weight_topic = np.array([x[1] for x in doc_topics])
        weight_word = query['weight']
        weight_word_dic = {}
        for i in range(len(query['query'])):
            weight_word_dic[query['query'][i]] = weight_word[i]
        for candidate in candidates:
            sim = self.__similarity(query['query'], weight_topic, weight_word_dic, candidate)
            sims[candidate['question_id']] = sim
        return sorted(sims.items(), lambda x, y: cmp(x[1], y[1]), reverse=True)

    def __similarity(self, query, weight_topic, weight_word_dic, candidate):
        """
        计算相似度，对求积取对数
        :param query: 查询
        :param weight_topic: 主题权重
        :param weight_word_dic: 词项权重
        :param candidate: 候选问题，带多个回答
        :return: 相似度
        """
        sim = -9999999.9
        length_q = len(candidate['question'])
        lam = 1.0 / (length_q + 1)
        question = Counter(candidate['question'])
        for answer in candidate['answers']:
            temp = 0
            for word in query:
                temp_w = 0
                if word in question and length_q != 0:
                    temp_w = self.parameters['mu1'] * weight_word_dic[word] * question[word] / length_q
                if self.translation_dic is not None and word in self.translation_dic and length_q != 0:
                    temp_t = 0
                    for x in question:
                        if x in self.translation_dic[word]:
                            temp_t = temp_t + self.translation_dic[word][x] * question[x]
                    temp_w = temp_w + self.parameters['mu2'] * temp_t / length_q
                if word in self.id2word_dic.token2id and length_q != 0:  # word在id2word_dic中
                    word_topics = np.multiply(weight_topic, self.matrix[:, self.id2word_dic.token2id[word]])
                    question_bow = self.id2word_dic.doc2bow(candidate['question'])
                    if len(question_bow) > 0:
                        question_matrix = self.matrix[:, [x[0] for x in question_bow]].T
                        question_cnt = np.array([x[1] for x in question_bow])
                        temp_t = np.sum(np.multiply(question_matrix.dot(word_topics), question_cnt))
                        temp_w = temp_w + self.parameters['mu3'] * temp_t / length_q
                length_a = len(answer)
                answer = Counter(answer)
                if word in answer and length_a != 0:
                    temp_w = temp_w + self.parameters['mu4'] * weight_word_dic[word] * answer[word] / length_a
                temp = temp + math.log(temp_w * (1 - lam) + self.background_dic[word] * lam)

            if temp > sim:
                sim = temp
        return sim
