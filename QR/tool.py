#!/usr/bin/python
# -*- coding: UTF-8 -*-

import codecs
import MySQLdb


def set_similarity(seq1, seq2):
    """
    计算两个序列的词汇重合度
    :param seq1: 序列1
    :param seq2: 序列2
    :return: 词汇重合度
    """
    set1 = set(seq1)
    set2 = set(seq2)
    return float(len(set1 & set2)) / len(set1 | set2)


class DBtool(object):

    def __init__(self):
        """
        初始化连接
        """
        self.db = MySQLdb.connect("127.0.0.1", "test", "password", "question_answer")

    def close(self):
        """
        关闭数据库连接
        :return:
        """
        self.db.close()

    def execute_select(self, sql):
        """
        执行查询语句
        :param sql: 查询语句
        :return: 查询结果
        """
        # 确保是查询
        # assert sql.startWith('s')
        cursor = self.db.cursor()
        data = None
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print e.message
        return data

    def select_relevance_flag(self, query_id, candidate_id):
        """
        获取相关性
        :param query_id: 查询ID
        :param candidate_id: 获选问题ID
        :return: 相关性和标记次数
        """
        cursor = self.db.cursor()
        data = None
        sql = "select relevance, flag from candidate where query_id=%d and candidate_id=%d" % (query_id, candidate_id)
        try:
            cursor.execute(sql)
            data = cursor.fetchall()
            if len(data) == 0:
                return None
            cursor.close()
        except Exception as e:
            print e.message
        return data[0]

    def select_queries(self):
        """
        获取所有查询
        :return: 查询列表[{'query_id': id, 'query': query}, ...]
        """
        cursor = self.db.cursor()
        cursor.execute('SET NAMES UTF8')
        queries = None
        sql = "select question_id, question from qa where question_id in (select id from query) group by question_id"
        try:
            cursor.execute(sql)
            queries = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print e.message
        queries = [{'query_id': x[0], 'query': x[1]} for x in queries]
        return queries

    def select_segmented_queries(self):
        """
        获取所有查询，已分好词
        :return: 查询列表[{'query_id': id, 'query': [word,...]},...]
        """
        cursor = self.db.cursor()
        cursor.execute('SET NAMES UTF8')
        queries = None
        sql = "select id, segmented_query from query order by id"
        try:
            cursor.execute(sql)
            queries = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print e.message
        queries = [{'query_id': x[0], 'segmented_query': x[1]} for x in queries]
        return queries

    def select_segmented_queries_weight(self):
        """
        获取所有查询，已分好词
        :return: 查询列表[{'query_id': id, 'query': [word,...], 'weight1': [], 'weight2': [],},...]
        """
        cursor = self.db.cursor()
        cursor.execute('SET NAMES UTF8')
        queries = None
        sql = "select id, segmented_query, weight_tf_idf, weight_ie, weight_topic from query order by id"
        try:
            cursor.execute(sql)
            queries = cursor.fetchall()
            cursor.close()
        except Exception as e:
            print e.message
        queries = [{'query_id': x[0],
                    'query': x[1].strip().split(' '),
                    'weight_tf_idf': [float(y) for y in x[2].strip().split(' ')],
                    'weight_ie': [float(y) for y in x[3].strip().split(' ')],
                    'weight_topic':  [float(y) for y in x[4].strip().split(' ')]} for x in queries]
        return queries

    def select_candidates(self, query_id):
        """
        根据查询ID获取其所有候选，包括id和文本
        :param query_id: 查询id
        :return: 候选列表 [{'question': 'q1', 'question_id': id, 'answers': ['a1', ...]}, ...]
        """
        cursor = self.db.cursor()
        cursor.execute('SET NAMES UTF8')
        candidates = []
        sql = "select question,question_id,answer from qa where question_id in " \
              "(SELECT candidate_id FROM candidate where query_id=%d) order by question_id" % query_id
        try:
            cursor.execute(sql)
            qa = cursor.fetchall()
            for x in qa:
                if len(candidates) == 0 or x[1] != candidates[-1]['question_id']:
                    candidates.append({'question': x[0], 'question_id': x[1], 'answers': [x[2]]})
                else:
                    candidates[-1]['answers'].append(x[2])
            cursor.close()
        except Exception as e:
            print e.message
        return candidates

    def update_segmented_query(self, query_id, segmented_query):
        """
        更新查询的分词结果
        :param query_id: 查询ID
        :param segmented_query: 分词结果
        :return:
        """
        cursor = self.db.cursor()
        sql = u"update query set segmented_query=%s where id=%s"
        try:
            cursor.execute(sql, (segmented_query, query_id))
            self.db.commit()
            cursor.close()
        except Exception as e:
            print e.message
            self.db.rollback()

    def update_weight(self, query_id, weight, weight_flag):
        """
        更新查询的分词结果
        :param query_id: 查询ID
        :param weight: 权重字符串
        :param weight_flag: 指定哪种权重
        :return:
        """
        cursor = self.db.cursor()
        sql = "update query set " + weight_flag + "=%s where id=%s"
        try:
            cursor.execute(sql, (weight, query_id))
            self.db.commit()
            cursor.close()
        except Exception as e:
            print e.message
            self.db.rollback()

    def update_flag(self, query_id, candidate_id, flag):
        """
        更新flag
        :param query_id: 查询ID
        :param candidate_id: 获选问题ID
        :param flag: 标准位
        :return:
        """
        cursor = self.db.cursor()
        sql = "update candidate set flag=%d where query_id=%d and candidate_id=%d" % (flag, query_id, candidate_id)
        try:
            cursor.execute(sql)
            self.db.commit()
            cursor.close()
        except Exception as e:
            print e.message
            self.db.rollback()

    def update_relevance(self, query_id, candidate_id, relevance):
        """
        更新relevance
        :param query_id: 查询ID
        :param candidate_id: 获选问题ID
        :param relevance: 相关度
        :return:
        """
        cursor = self.db.cursor()
        sql = "update candidate set relevance=%d, flag=1 where query_id=%d and candidate_id=%d" \
              % (relevance, query_id, candidate_id)
        try:
            cursor.execute(sql)
            self.db.commit()
            cursor.close()
        except Exception as e:
            print e.message
            self.db.rollback()

    def insert_candidate(self, query_id, candidate_id):
        """
        插入未标记表
        :param query_id: 查询ID
        :param candidate_id: 获选问题ID
        :return:
        """
        cursor = self.db.cursor()
        sql = "insert ignore into candidate(query_id, candidate_id) values (%d, %d)" % (query_id, candidate_id)
        try:
            cursor.execute(sql)
            self.db.commit()
            cursor.close()
        except Exception as e:
            print e.message
            self.db.rollback()

    def insert_qa(self, qa_pairs):
        """
        插入多条问答对
        :param qa_pairs:问答数据的列表
        :return: 影响行数
        """
        qa_pairs = [x for x in qa_pairs if len(x) == 6]
        cursor = self.db.cursor()
        sql = "insert ignore into qa(question_id, questioner_id, question, answer_id, answerer_id, answer) values " \
              "(%s, %s, %s, %s, %s, %s)"
        num = 0
        try:
            num = cursor.executemany(sql, qa_pairs)
            self.db.commit()
            cursor.close()
        except Exception as e:
            print e.message
        return num

    def insert_user(self, users):
        """
        插入多条问答对
        :param users:问答数据的列表
        :return: 影响行数
        """
        users = [x for x in users if len(x) == 4]
        cursor = self.db.cursor()
        sql = "insert ignore into user(id, askCnt, ansCnt, adopt) values (%s, %s, %s, %s)"
        num = 0
        try:
            num = cursor.executemany(sql, users)
            self.db.commit()
            cursor.close()
        except Exception as e:
            print e.message
        return num


class WordFilter(object):
    def __init__(self, dic_path='F:/Data/Chinese/dic', min_tf=5):
        """
        初始分词工具
        """
        self.dictionary = set()
        with codecs.open(dic_path, 'r', 'utf-8') as f:
            for line in f:
                word = line.strip().split('\t')
                if len(word) == 2 and int(word[1]) >= min_tf:
                    self.dictionary.add(word[0])
        # 只保留文本部分，并分词，根据词性过滤
        # 保留以下词性的词，并去除词性标记
        # 词性含义请查看https://github.com/tsroten/pynlpir/blob/master/pynlpir/pos_map.py
        self.word_filter = {'noun', 'time word', 'locative word', 'noun of locality', 'verb',
                            'adjective', 'distinguishing word', 'status word', 'numeral'}

    def filter(self, words):
        """
        分词
        :param words: pynlpir初步分词的结果
        :return: 过滤后结果
        """
        return [w[0] for w in words if w[1] in self.word_filter and w[0] in self.dictionary]
