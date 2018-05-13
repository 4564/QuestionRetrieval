#!/usr/bin/env python
# -*- encoding:UTF-8 -*-

import json
import MySQLdb
import tool
import pynlpir
from collections import Counter
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim')
from gensim.models import LdaModel
from gensim import corpora


# j = [[['a', 'b', 'c', 'd'],
#      ['a', 'b', 'c', 'e'],
#      ['a', 'b', 'c', 'f'],
#      ['a', 'b', 'c', 'f'],
#      ['a', 'b', 'c', 'g'],
#      ['a', 'b', 'c', 'd']]]
# 清除重复
# for x in range(len(j)):
#     temp = []
#     for i in range(len(j[x])):
#         flag = True
#         for k in range(i + 1, len(j[x])):
#             if tool.similarity_tool.set_similarity(j[x][i], j[x][k]) == 1:
#                 flag = False
#                 break
#         if flag:
#             temp.append(j[x][i])
#     j[x] = temp

# print j

'''
测试DBTOOL
word_filter = tool.WordFilter()
queries = db_tool.select_queries()
pynlpir.open()
# db_tool.update_segmented_query(5793896L, u"a 你 我 sf".encode('utf-8'))
for query in queries:
    query['query'] = ' '.join(word_filter.filter(pynlpir.segment(query['query']))).encode('utf-8')
    db_tool.update_segmented_query(query['query_id'], query['query'])
pynlpir.close()
db_tool.close()
db_tool = tool.DBtool()
with open('F:/Data/Chinese/relevance.txt', 'r') as f:
    for line in f:
        relevance = line.strip().split(' ')
        assert len(relevance) == 3
        db_tool.update_relevance(int(relevance[0]), int(relevance[1]), int(relevance[2]))
db_tool.close()
'''

# users = set()
# with open('F:/Data/Chinese/BestAnswerUser.csv', 'r') as f:
#     for line in f:
#         user = int(line.strip())
#         users.add(user)
# print len(users)
#
# db_tool = tool.DBtool()
# best = []
# for user in users:
#     data = db_tool.execute_select('select round(ansCnt*adopt) as adopt_num from user where id=%d' % user)
#     best.append(int(data[0][0]) - 1)
# print len(best)
# best = [x for x in best if x >= 0]
# best = Counter(best)
# best = [(x, best[x]) for x in best]
# le = float(sum([x[1] for x in best if x[0] < 400]))
# s = sum([x[0]*x[1] for x in best if x[0] < 400])
# print s / le
# best = best[1:11]
# adopt_numbers = [x[0] for x in best]
# proportion = [100 * x[1] / le for x in best]
# plt.plot(adopt_numbers, proportion, '*:', markersize=15, label=u'最佳回答者')
#
# sql_all = 'select round(ansCnt*adopt) as adopt_num, count(round(ansCnt*adopt)) as cnt from user ' \
#           'where id in ' \
#           '(select answerer_id from qa where question_id in (select candidate_id from candidate where flag=1) ' \
#           'group by answerer_id) group by adopt_num order by adopt_num'
# sql_unrel = 'select round(ansCnt*adopt) as adopt_num, count(round(ansCnt*adopt)) as cnt from user ' \
#           'where id in ' \
#           '(select answerer_id from qa where question_id in (select candidate_id from candidate where flag=1 and relevance=0) ' \
#           'group by answerer_id) group by adopt_num order by adopt_num'
# sql_rel = 'select round(ansCnt*adopt) as adopt_num, count(round(ansCnt*adopt)) as cnt from user ' \
#           'where id in ' \
#           '(select answerer_id from qa where question_id in (select candidate_id from candidate where flag=1 and relevance=1) ' \
#           'group by answerer_id) group by adopt_num order by adopt_num'
# data = db_tool.execute_select(sql_all)
# if data is not None:
#     length = float(sum([x[1] for x in data if x[0] < 400]))
#     data = data[1:11]
#     adopt_numbers = [int(x[0]) for x in data]
#     proportion = [100 * x[1] / length for x in data]
#     plt.plot(adopt_numbers, proportion, 'x-', markersize=15, label=u'全体用户')
# data = db_tool.execute_select(sql_unrel)
# if data is not None:
#     length = float(sum([x[1] for x in data if x[0] < 400]))
#     s = sum([x[0]*x[1] for x in data if x[0] < 400])
#     data = data[1:11]
#     adopt_numbers = [int(x[0]) for x in data]
#     proportion = [100 * x[1] / length for x in data]
#     plt.plot(adopt_numbers, proportion, 'v--', markersize=15, label=u'相关候选提问者')
# data = db_tool.execute_select(sql_rel)
# if data is not None:
#     length = float(sum([x[1] for x in data if x[0] < 400]))
#     s = sum([x[0]*x[1] for x in data if x[0] < 400])
#     data = data[1:11]
#     adopt_numbers = [int(x[0]) for x in data]
#     proportion = [100 * x[1] / length for x in data]
#     plt.plot(adopt_numbers, proportion, '^-.', markersize=15, label=u'无关候选提问者')
# plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
# plt.xticks(fontsize=30)
# plt.yticks(fontsize=30)
# ax = plt.subplot(111)
# ax.set_xlabel(u'最佳回答数', fontsize=30)
# ax.set_ylabel(u'占比(%)', fontsize=30)
# legend = plt.legend(loc='upper right', prop={'size': 40}, shadow=True, fontsize='x-large')
# plt.show()

"""
最佳回答的召回率
question_ids = set()
with open('F:/Data/Chinese/b.txt', 'r') as f:
    for line in f:
        question_id = int(line.strip())
        question_ids.add(question_id)
print len(question_ids)

temp = {}
with open('F:/Data/Chinese/c.txt', 'r') as f:
    for line in f:
        word = line.strip().split('\t')
        if int(word[0]) in question_ids:
            temp[int(word[0])] = int(word[1])
print len(temp)
question_ids = temp

db_tool = tool.DBtool()
rank = []
for question_id in question_ids:
    # 获得其排序
    sql = 'SELECT answerer_id, round(ansCnt *adopt) as score FROM qa,user ' \
          'where qa.answerer_id=user.id and question_id=%d order by score desc'
    data = db_tool.execute_select(sql % question_id)
    for i in range(len(data)):
        if data[i][0] == question_ids[question_id]:
            if i == 0 or data[i][1] >= 400:
                rank.append(1)
            elif data[i][1] == data[0][1]:
                rank.append(1)
            else:
                # 往前探
                for j in range(i - 1, -1, -1):
                    if data[i][1] != data[j][1]:
                        rank.append(j + 2)
                        break
            break
    pass

rank1 = len([x for x in rank if x == 1]) / float(len(rank))
rank2 = len([x for x in rank if x < 3]) / float(len(rank))
rank3 = len([x for x in rank if x < 4]) / float(len(rank))
print rank1, rank2, rank3
"""
