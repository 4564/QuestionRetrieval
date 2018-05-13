#!/usr/bin/python
# -*- coding: UTF-8 -*-

import os
import tool


def load_result(result_path):
    """
    载入result
    :param result_path: 结果路径
    :return: queries
    """
    print "读取结果："
    print result_path
    result = []
    with open(result_path, 'r') as f:
        for line in f:
            temp = line.strip().split('\t')
            if len(temp) != 11:
                print "%s不满10个" % temp[0]
            query_id = long(temp[0])
            candidate_ids = [long(x) for x in temp[1:]]
            result.append({'query_id': query_id, 'candidate_ids': candidate_ids})
    print "获取相关度"
    # 要换了，flag=4的才算，0就变-1，其他的不用管了
    db_tool = tool.DBtool()
    count = 0
    for query in result:
        query_id = query['query_id']
        relevance = []
        for candidate_id in query['candidate_ids']:
            rs = db_tool.select_relevance_flag(query_id, candidate_id)
            if rs is None:
                relevance.append(0)
                # 插入candidate表和标记为需标记候选
                db_tool.insert_candidate(query_id, candidate_id)
                db_tool.update_flag(query_id, candidate_id, -1)
                count = count + 1
            elif rs[1] == 4:
                relevance.append(rs[0])
            else:
                count = count + 1
                relevance.append(0)
                if rs[1] == 0:
                    # 标记为需标记候选
                    db_tool.update_flag(query_id, candidate_id, -1)
        query['relevance'] = relevance
    db_tool.close()
    if count != 0:
        print '有%d个候选问题相关性未标记，此次计算被自动设置为0，请标记后在重新计算！' % count
    return result


def p_at_n(result, n):
    """
    计算结果result的P@N
    :param result: 带相关度的结果
    :param n: N
    :return: P@N
    """
    # 计算结果
    count = 0
    for query in result:
        query['relevance'] = query['relevance'][0:n]
        for rel in query['relevance']:
            if rel > 0:
                count = count + 1
    return float(count) / len(result) * n


def map_at_n(result, n):
    """
    计算结果result的MAP@N
    :param result: 带相关度的结果
    :param n: N
    :return: MAP@N
    """
    temp = 0.0
    for query in result:
        query['relevance'] = query['relevance'][0:n]
        count = 0
        for i in range(n):
            if query['relevance'][i] > 0:
                count = count + 1
                temp = temp + float(count) / (i + 1)
    return temp / len(result)


def ndcg_at_n(result, n):
    """
    计算结果result的NDCG@N
    :param result: 带相关度的结果
    :param n: N
    :return: NDCG@N
    """


if __name__ == '__main__':
    path = 'F:/Data/Chinese/Result/'
    file_list = [os.path.join(path, x) for x in os.listdir(path) if x.endswith('.tsv')]
    for f in file_list:
        res = load_result(f)
        # 计算跟保存
