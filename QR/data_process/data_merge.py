#!/usr/bin/env python
# -*- encoding:UTF-8 -*-

import json
import random
import time


def merge(file_list, json_path='F:/Data/Chinese/chinese.json'):
    """
    融合数据分配统一id
    :return:
    """
    start = time.time()
    print '处理:'
    res = []
    temp = []
    for file_path in file_list:
        print file_path
        with open(file_path, 'r') as f:
            for line in f:
                j = json.loads(line)
                if 'question_id' in j:
                    res.append(j)
                else:
                    temp.append(j)
    print time.time() - start

    start = time.time()
    # 取得qid集合
    qids = set([x['question_id'] for x in res])
    print time.time() - start

    start = time.time()
    # 取得aid集合
    aids = set()
    for x in res:
        for y in x['answers']:
            aids.add(y['answer_id'])
    print time.time() - start

    start = time.time()
    # 为无id的分配id
    for x in temp:
        new_qid = random.randint(1000000, 9999999)
        while new_qid in qids:
            new_qid = random.randint(1000000, 9999999)
        x['question_id'] = new_qid
        qids.add(new_qid)
        x['questioner_id'] = -1
        for y in x['answers']:
            new_aid = random.randint(10000000, 99999999)
            while new_aid in aids:
                new_aid = random.randint(1000000, 9999999)
            y['answer_id'] = new_aid
            aids.add(new_aid)
            y['answerer_id'] = -1
    print time.time() - start

    res[len(res):len(res)] = temp

    # 写入文件
    f = open(json_path, 'w')
    for x in res:
        f.write(json.dumps(x))
        f.write('\n')
    f.close()
    print '融合结果已保存到:'
    print json_path


if __name__ == '__main__':
    """
    将抽取出的数据融合，解决非sogou数据的
    """
    # data_paths = ['F:/Data/Chinese/Sogou/QA/sogou.json',
    #               'F:/Data/Chinese/NLPCC/2016QA/train/nlpcc2016.json',
    #               'F:/Data/Chinese/Baidu/WebQA.v1.0/data/baidu_webqa.json',
    #               'F:/Data/Chinese/Baidu/Reading Comprehension/raw/baidu_reading_comprehension.json']
    # merge(data_paths)
