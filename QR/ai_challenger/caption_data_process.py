#!/usr/bin/env python
# -*- encoding:UTF-8 -*-

import os
import json
import pynlpir
import tool
import sys
import codecs

path = 'F:/Data/Chinese/AI_Challenger/caption'
json_path = 'F:/Data/Chinese/AI_Challenger/caption.json'
corpus_path = 'F:/Data/Chinese/AI_Challenger'
# 相似度限制
# similarity_limit = 0.25


def segment_filter():
    """
    原始文件分词并过滤
    :return:
    """
    # 获取文件列表
    file_list = os.listdir(path)
    # file_list = ['caption_validation_annotations_20170910.json']

    res = []  # 结果列表

    # 启动分词工具
    pynlpir.open()
    for file_name in file_list:
        file_path = os.path.join(path, file_name)
        # 打开文件
        f = open(file_path, 'r')
        # 载入json,文件只有一行，一个json
        j = json.loads(f.readline())
        # j = j[:100]
        # 只取caption部分
        j = [x['caption'] for x in j]
        # 分词
        j = [[y.replace('\n', ' ') for y in x] for x in j]
        j = [[pynlpir.segment(y) for y in x] for x in j]
        # 根据词性清洗词
        # 保留以下词性的词，并去除词性标记
        # 词性含义请查看https://github.com/tsroten/pynlpir/blob/master/pynlpir/pos_map.py
        word_filter = ('noun', 'time word', 'locative word', 'noun of locality', 'verb', 'adjective',
                       'distinguishing word', 'status word', 'numeral', 'adverb')
        j = [[[z[0] for z in y if z[1] in word_filter] for y in x] for x in j]

        # 去除为空的句子
        j = [[y for y in x if len(y) != 0] for x in j]

        # 清除重复
        for x in range(len(j)):
            temp = []
            for i in range(len(j[x])):
                flag = True
                for k in range(i + 1, len(j[x])):
                    temp_set1 = set(j[x][i])
                    temp_set2 = set(j[x][k])
                    if len(temp_set1 | temp_set2) == len(temp_set1 & temp_set2):
                        flag = False
                        break
                if flag:
                    temp.append(j[x][i])
            j[x] = temp
        # 加到结果集
        res[len(res):len(res)] = j
    pynlpir.close()
    print '分词完成'

    # 保存到json文件
    res = [{'caption': x} for x in res]
    # 保存到json对象
    json_obj = json.dumps(res)
    # 写入文件
    f = open(json_path, 'w')
    f.write(json_obj)
    f.close()
    print '存入json文件：%s' % json_path


def json2corpus(similarity_limit):
    """
    读取json文件根据重合度转换为平行语料
    :return:
    """
    f_in = open(json_path, 'r')
    # 载入json,文件只有一行，一个json
    j = json.loads(f_in.readline())
    # j = j[:1]
    # 只取caption部分
    j = [x['caption'] for x in j]
    f_out_source = codecs.open(os.path.join(corpus_path, str(similarity_limit), 'S'), 'w', 'utf-8')
    f_out_target = codecs.open(os.path.join(corpus_path, str(similarity_limit), 'T'), 'w', 'utf-8')
    for e in j:
        for x in range(len(e)):
            for y in range(x + 1, len(e)):
                if tool.similarity_tool.set_similarity(e[x], e[y]) <= similarity_limit:
                    f_out_source.write(' '.join(e[x]))
                    f_out_source.write(' \n')
                    f_out_target.write(' '.join(e[y]))
                    f_out_target.write(' \n')
    f_out_source.close()
    f_out_target.close()


def pool(similarity_limit):
    """
    对平行语料进行pool操作
    :return:
    """
    f_out_source = codecs.open(os.path.join(corpus_path, str(similarity_limit), 'Sp'), 'w')
    f_in_target = codecs.open(os.path.join(corpus_path, str(similarity_limit), 'T'), 'r')
    f_in_source = codecs.open(os.path.join(corpus_path, str(similarity_limit), 'S'), 'r')
    f_out_source.writelines(f_in_source.read())
    f_out_source.writelines(f_in_target.read())
    f_out_source.close()
    f_in_source.seek(0)
    f_in_target.seek(0)
    f_out_target = codecs.open(os.path.join(corpus_path, str(similarity_limit), 'Tp'), 'w')
    f_out_target.write(f_in_target.read())
    f_out_target.write(f_in_source.read())
    f_out_target.close()
    f_in_source.close()
    f_in_target.close()


if __name__ == '__main__':
    """
    把AI Challenger的Caption数据处理成分词好的平行语料
    """
    segment_filter()
    json2corpus(0.25)
    pool(0.25)
