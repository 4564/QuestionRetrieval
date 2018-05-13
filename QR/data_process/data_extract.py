#!/usr/bin/env python
# -*- encoding:UTF-8 -*-

import os
import re
import json
import codecs


def extract_sogou_user(path='F:/Data/Chinese/Sogou/QA'):
    """
    融合file_list中源数据，保存同一目录下sogou_user.json文件中
    用户id，提问数，回答数，采纳率
    :param path: 源数据目录
    :return:
    """
    print '抽取:'
    res = []
    id_set = set()
    file_path = os.path.join(path, u'用户属性数据集')
    print file_path
    with open(file_path, 'r') as f:
        for line in f:
            w = line.strip().split('\t')
            assert len(w) == 4
            user = {'id': long(w[0]), 'askCnt': int(w[1]), 'ansCnt': int(w[2]), 'adopt': float(w[3]) / 100}

            # 处理异常数据
            if user['askCnt'] < 0:
                user['askCnt'] = -user['askCnt']
            if user['ansCnt'] < 0:
                user['ansCnt'] = -user['ansCnt']
            if user['adopt'] < 0:
                # 转正后只留小数部分
                user['adopt'] = -user['adopt'] + int(user['adopt'])
            if user['adopt'] > 1:
                # 只留小数部分
                user['adopt'] = user['adopt'] - int(user['adopt'])
            if user['adopt'] == 1 and user['ansCnt'] > 50:
                # 只留小数部分
                user['adopt'] = 0

            if user['id'] not in id_set:
                res.append(user)
                id_set.add(user['id'])

    file_path = os.path.join(path, 'user.info')
    print file_path
    with open(file_path, 'r') as f:
        for line in f:
            w = line.strip().split('\t')
            assert len(w) == 4
            user = {'id': long(w[0]), 'askCnt': int(w[1]), 'ansCnt': int(w[2]), 'adopt': float(w[3])}

            # 处理异常数据
            if user['askCnt'] < 0:
                user['askCnt'] = -user['askCnt']
            if user['ansCnt'] < 0:
                user['ansCnt'] = -user['ansCnt']
            if user['adopt'] < 0:
                # 转正后只留小数部分
                user['adopt'] = -user['adopt'] + int(user['adopt'])
            if user['adopt'] > 1:
                # 只留小数部分
                user['adopt'] = user['adopt'] - int(user['adopt'])
            if user['adopt'] == 1 and user['ansCnt'] > 50:
                # 只留小数部分
                user['adopt'] = 0

            if user['id'] not in id_set:
                res.append(user)
                id_set.add(user['id'])

    # 写入文件
    json_path = os.path.join(path, 'sogou_user.json')
    f = open(json_path, 'w')
    for x in res:
        f.write(json.dumps(x))
        f.write('\n')
    f.close()
    print '抽取结果已保存到:'
    print json_path


def extract_sogou(path='F:/Data/Chinese/Sogou/QA', file_list=[u'推广数据集', u'实验数据集', 'pingce.data']):
    """
    融合file_list中源数据，去掉不要的部分重新统一保存同一目录下sogou.json文件中
    主要保留问题id，提问者id，问题，回答id，回答者id，回答
    :param path: 源数据目录
    :param file_list: 源数据文件名列表
    :return:
    """
    print '抽取:'
    res = {}
    file_list = [os.path.join(path, x) for x in file_list]
    for file_path in file_list:
        print file_path
        with codecs.open(file_path, 'r', 'utf-8') as f:
            # 多行，每行依次是
            #   0       1         2       3          4         5            6     7       8    9    10 11      12
            # qid,askerID,askerNick,askerIP,offerScore,beginTime,askAnonymous,title,replyId,uind,unick,ip,endTime,
            #           13      14           15
            # uniAnonymous,content,isBestAnswer
            for line in f:
                qa = line.split('\t')
                if len(qa) == 16:
                    if qa[0] in res:
                        flag = True
                        for x in res[qa[0]]['answers']:
                            if long(qa[8]) == x['answer_id']:
                                flag = False
                                break
                        if flag:
                            res[qa[0]]['answers'].append({'answer_id': long(qa[8]),
                                                          'answerer_id': long(qa[9]),
                                                          'answer': qa[14]})
                    else:
                        res[qa[0]] = {'question_id': long(qa[0]),
                                      'questioner_id': long(qa[1]),
                                      'question': qa[7],
                                      'answers': [{'answer_id': long(qa[8]),
                                                   'answerer_id': long(qa[9]),
                                                   'answer': qa[14]}]}
    res = res.values()

    # 写入文件
    json_path = os.path.join(path, 'sogou.json')
    f = open(json_path, 'w')
    for x in res:
        f.write(json.dumps(x))
        f.write('\n')
    f.close()
    print '抽取结果已保存到:'
    print json_path


def extract_nlpcc2016(path='F:/Data/Chinese/NLPCC/2016QA/train'):
    """
    把2016的train中kbqa和dbqa数据去掉不要的部分重新统一保存到同一目录的nlpcc2016.json中
    这里只保留问题和回答
    :param path: kbqa和dbqa数据所在目录
    :return:
    """
    print '抽取:'
    dbqa = []
    file_path = os.path.join(path, 'nlpcc-iccpol-2016.dbqa.training-data')
    print file_path
    with open(file_path, 'r') as f:
        for line in f:
            dbqa.append(line.strip().split('\t'))

    res = [{'question': x[0], 'answers': [{'answer': x[1]}]} for x in dbqa if x[2] == '1']

    kbqa = None
    file_path = os.path.join(path, 'nlpcc-iccpol-2016.kbqa.training-data')
    print file_path
    with open(file_path, 'r') as f:
        s = f.read()
        reg = re.compile("(?<=question id=)(\d+)(?=>).*?(?<=\t)([^\n]*).*?(?<=\t)([^\n]*)", re.I | re.M | re.S)
        kbqa = re.findall(reg, s)

    res[len(res):len(res)] = [{'question': x[1], 'answers': [{'answer': x[2]}]} for x in kbqa]

    # 写入文件
    json_path = os.path.join(path, 'nlpcc2016.json')
    f = open(json_path, 'w')
    for x in res:
        f.write(json.dumps(x))
        f.write('\n')
    f.close()
    print '抽取结果已保存到:'
    print json_path


def extract_baidu_webqa(path='F:/Data/Chinese/Baidu/WebQA.v1.0/data'):
    """
    融合train,valid,test数据去掉不要的部分重新统一保存
    :return:
    """
    # 已经存在结果数据，先删除
    json_path = os.path.join(path, 'baidu_webqa.json')
    if os.path.exists(json_path):
        print '删除:'
        print json_path
        os.remove(json_path)

    print '抽取:'
    res = []
    file_list = os.listdir(path)
    # file_list = ['test.ann.json']
    file_list = [os.path.join(path, f) for f in file_list if f.endswith('.json')]
    for file_path in file_list:
        print file_path
        with open(file_path, 'r') as f:
            # 载入json,文件有多行，多个json
            for line in f:
                j = json.loads(line)
                res.append({  # u'question_id': j[u'q_key'],
                            u'question': ''.join(j[u'question_tokens']),
                            u'answers': [{  # u'answer_id': y[u'e_key'],
                                          u'answer': ''.join(y[u'evidence_tokens'])}
                                         for y in j[u'evidences']]})

    # 消耗过多内存
    # res = [{u'q_key': x[u'q_key'],
    #        u'question_tokens': x[u'question_tokens'],
    #        u'evidences': [{u'e_key': y[u'e_key'], u'evidence_tokens': y[u'evidence_tokens']}
    #           for y in x[u'evidences']]} for x in res]

    # 写入文件
    f = open(json_path, 'w')
    for x in res:
        f.write(json.dumps(x))
        f.write('\n')
    f.close()
    print '抽取结果已保存到:'
    print json_path


def extract_baidu_reading_comprehension(path='F:/Data/Chinese/Baidu/Reading Comprehension/raw'):
    """
    融合train,valid,test数据去掉不要的部分重新统一保存
    :return:
    """
    print '提取:'
    res = []
    dir_list = os.listdir(path)
    # 提取文件夹，保存路径
    dir_list = [os.path.join(path, x) for x in dir_list if os.path.isdir(os.path.join(path, x))]

    for d in dir_list:
        # 进入文件夹，处理json文件
        for file_path in [os.path.join(d, x) for x in os.listdir(d) if x.endswith('.json')]:
            print file_path
            with open(file_path, 'r') as f:
                # 载入json,文件有多行，多个json
                for line in f:
                    j = json.loads(line)
                    # 清除不要的
                    # key_filter = ['documents', 'entity_answers', 'fact_or_opinion', 'question_type']
                    # for k in key_filter:
                    #     if k in j:
                    #         del j[k]
                    # 保留要的 去除回答为空的
                    if 'question_id' in j and 'question' in j and 'answers' in j and len(j['answers']) > 0:
                        # 确认无异常空数据
                        # if len(j['question']) == 0:
                        #     print j['question_id']
                        # for x in j['answers']:
                        #     if len(x) == 0:
                        #         print j['question_id'] + '#answer'
                        res.append({  # 'question_id': j['question_id'],
                                    'question': j['question'],
                                    'answers': [{'answer': x} for x in j['answers']]})

    # 写入文件
    json_path = os.path.join(path, 'baidu_reading_comprehension.json')
    f = open(json_path, 'w')
    for x in res:
        f.write(json.dumps(x))
        f.write('\n')
    f.close()
    print '抽取结果已保存到:'
    print json_path


if __name__ == '__main__':
    """
    处理NDBC CUP 2016中sogou数据中的user.info和用户属性数据集
    """
    # extract_sogou_user()

    """
    处理NDBC CUP 2016中sogou数据中的pingce.data, 推广数据集, 实验数据集
    """
    # extract_sogou()

    """
    把2016的train中kbqa和dbqa数据
    """
    # extract_nlpcc2016()

    """
    把Baidu webqa的train,valid,test数据去掉不要的部分重新统一保存
    """
    # extract_baidu_webqa()

    """
    把Baidu reading comprehension的train,dev,test数据去掉不要的部分重新统一保存
    """
    # extract_baidu_reading_comprehension()
