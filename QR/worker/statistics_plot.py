#!/usr/bin/env python
# -*- encoding:UTF-8 -*-

import tool
import matplotlib.pyplot as plt


def user_adopt_distribution():
    """
    用户的最佳回答数分布
    :return:
    """
    sql_all = "select round(ansCnt*adopt) as adopt_number, count(round(ansCnt*adopt)) as cnt from user " \
              "group by adopt_number order by adopt_number"
    sql_ask = "select round(ansCnt*adopt) as adopt_number, count(round(ansCnt*adopt)) as cnt from user " \
              "where id in (SELECT distinct(questioner_id) FROM qa where questioner_id != -1) " \
              "group by adopt_number order by adopt_number"
    sql_answer = "select round(ansCnt*adopt) as adopt_number, count(round(ansCnt*adopt)) as cnt from user " \
                 "where id in (SELECT distinct(answerer_id) FROM qa where answerer_id != -1) " \
                 "group by adopt_number order by adopt_number"
    db_tool = tool.DBtool()
    data = db_tool.execute_select(sql_all)
    if data is not None:
        length = float(sum([x[1] for x in data]))
        print length
        print data[0][1] / length
        data = data[1:11]
        adopt_numbers = [int(x[0]) for x in data]
        proportion = [100 * x[1] / length for x in data]
        plt.plot(adopt_numbers, proportion, 'x-', markersize=15, label=u'全体用户')
    data = db_tool.execute_select(sql_ask)
    if data is not None:
        length = float(sum([x[1] for x in data]))
        print length
        print data[0][1] / length
        data = data[1:11]
        adopt_numbers = [int(x[0]) for x in data]
        proportion = [100 * x[1] / length for x in data]
        plt.plot(adopt_numbers, proportion, 'v--', markersize=15, label=u'提问者')
    data = db_tool.execute_select(sql_answer)
    if data is not None:
        length = float(sum([x[1] for x in data]))
        print length
        print data[0][1] / length
        data = data[1:11]
        adopt_numbers = [int(x[0]) for x in data]
        proportion = [100 * x[1] / length for x in data]
        plt.plot(adopt_numbers, proportion, '^-.', markersize=15, label=u'回答者')
    db_tool.close()
    plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    ax = plt.subplot(111)
    ax.set_xlabel(u'最佳回答数', fontsize=30)
    ax.set_ylabel(u'占比(%)', fontsize=30)
    legend = plt.legend(loc='upper right', prop={'size': 40}, shadow=True, fontsize='x-large')

    plt.show()


if __name__ == '__main__':
    '''
    统计最佳回答的分布情况
    '''
    user_adopt_distribution()
