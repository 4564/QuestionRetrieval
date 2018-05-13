#!/usr/bin/env python
# -*- encoding:UTF-8 -*-

import json
import tool


def export_qa_mysql(path='F:/Data/Chinese/chinese.json', filter_path='F:/Data/Chinese/chinese_token.json'):
    """
    问答数据导入数据库
    :param path: 数据路径
    :param filter_path: token数据路径，过滤依据
    :return:
    """
    print '读取过滤器:'
    print filter_path
    id_set = set()
    with open(filter_path, 'r') as f:
        for line in f:
            q = json.loads(line)
            for a in q['answers']:
                id_set.add(a['answer_id'])
    print len(id_set)

    db_tool = tool.DBtool()
    with open(path, 'r') as f:
        count = 0
        qa_pairs = []
        for line in f:
            count = count + 1
            q = json.loads(line)
            for a in q['answers']:
                if a['answer_id'] in id_set:
                    qa_pairs.append(
                        (q['question_id'],
                         q['questioner_id'],
                         q['question'].encode('utf-8'),
                         a['answer_id'],
                         a['answerer_id'],
                         a['answer'].encode('utf-8')))
            if count % 500 == 0:
                num = db_tool.insert_qa(qa_pairs)
                print '插入%d条数据, 失败%d条' % (len(qa_pairs), len(qa_pairs) - num)
                qa_pairs = []
        # 别忘了收尾
        num = db_tool.insert_qa(qa_pairs)
        print '插入%d条数据, 失败%d条' % (len(qa_pairs), len(qa_pairs) - num)
    db_tool.close()


def export_user_mysql(path='F:/Data/Chinese/Sogou/QA/sogou_user.json'):
    """
    用户数据导入数据库
    :param path: 数据路径
    :return:
    """
    db_tool = DBtool()
    with open(path, 'r') as f:
        count = 0
        users = []
        for line in f:
            count = count + 1
            j = json.loads(line)
            users.append((j['id'], j['askCnt'], j['ansCnt'], j['adopt']))
            if count % 20000 == 0:
                num = db_tool.insert_user(users)
                print '插入%d条数据, 失败%d条' % (len(users), len(users) - num)
                users = []
        # 别忘了收尾
        num = db_tool.insert_user(users)
        print '插入%d条数据, 失败%d条' % (len(users), len(users) - num)
    db_tool.close()


if __name__ == '__main__':
    """
    导入用户数据到数据库
    """
    # export_user_mysql()  # 'test_data.json'

    """
    导入问答数据到数据库
    """
    # export_qa_mysql()  # 'test_data.json'
