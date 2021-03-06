import wxpy
import re
import json
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


def insert_sort(v_lists, k_lists):
    # 插入排序
    count = len(v_lists)
    for i in range(1, count):
        v_key = v_lists[i]
        k_key = k_lists[i]
        j = i - 1
        while j >= 0:
            if v_lists[j] > v_key:
                v_lists[j + 1] = v_lists[j]
                k_lists[j + 1] = k_lists[j]
                v_lists[j] = v_key
                k_lists[j] = k_key
            j -= 1
    return v_lists, k_lists


def make_autopct(values):
    def my_autopct(pct):
        total = sum(values)
        val = int(round(pct * total / 100.0))
        return '{p:.1f}%({v:d})'.format(p=pct, v=val)

    return my_autopct


# implement a pie chart
def get_pie(a_plt, data, title=None):
    a_plt.clear()
    a_plt.axis("equal")
    pie_data = list(data.values())
    pie_labels = list(data.keys())
    a_plt.pie(pie_data, radius=1.25, labels=pie_labels,
              autopct=make_autopct(pie_data), pctdistance=0.65)
    a_plt.legend(loc='best')
    a_plt.set_title(title)


# implement a bar chart
def get_a_bar(a_plt, bar_data, title=None, if_sort=False):
    a_plt.clear()
    a_plt.set_ylabel('数量', fontsize=20)
    # a_plt.text(len(bar_data.keys()), -15, category, ha='center', va='bottom')  # x_label
    if if_sort:
        bar_values, bar_names = insert_sort(list(bar_data.values()), list(bar_data.keys()))
    else:
        bar_names = list(bar_data.keys())
        bar_values = list(bar_data.values())
    a_plt.set_ylim(0, max(bar_values) + 25)
    a_plt.bar(range(len(bar_values)), bar_values, tick_label=bar_names)
    # set the text of value
    index = range(len(bar_values))
    for i, j in zip(index, bar_values):
        a_plt.text(i, j + 2, j, ha='center', va='bottom')
    a_plt.set_title(title)


def get_bar_data(p_data, category):
    fore_num, other_num, unknown_num = 0, 0, 0
    bar_data = {}
    staring_num = 0.1 * max(p_data.values())  # 单独成为一个柱体的条件: >= 0.1*max_value
    for k, v in p_data.items():
        if re.match('[\u4e00-\u9fa5]+', k) \
                is not None and v >= staring_num:  # China(in Chinese char) province and eligible
            bar_data[k] = v
        elif re.match('[\u4e00-\u9fa5]+', k) \
                is not None:  # China(in Chinese char) province but ineligible
            other_num += v
        elif k == '':
            unknown_num += v
        else:
            fore_num += v  # foreign area
    if other_num != 0:
        bar_data["其他\n%s" % category] = other_num
    if fore_num != 0:
        bar_data['国外'] = fore_num
    if unknown_num != 0:
        bar_data['↑\nunknown'] = unknown_num
    return bar_data


def read_data_from_WeChat(Wechat_bot):
    # show and certify a group
    groups = Wechat_bot.groups()
    for k, v in enumerate(groups):
        print("%d、%s" % (k, v.name))
    s = int(input("选定一个群"))
    group = groups[s]

    # get group info/data
    group.update_group(True)
    print(group.members.stats_text())
    group_members_stat = group.members.stats()
    group_members_stat['group_name'] = group.name

    # save group_data to json file
    f = open('group_data.json', 'w')
    f.write(json.dumps(group_members_stat, indent=4))
    f.close()

    return group, group_members_stat


def is_int(val):
    try:
        int(val)
        return True
    except ValueError:
        return False


def read_data_from_file(data_file):
    group_members_stat = json.loads(data_file.read())

    class Group:
        name = group_members_stat['group_name']

    return Group, group_members_stat

# 提供两种方式获取数据，首先先要登陆微信获取一次数据【第一二三行】。
# 后来的启动，可以调用read_data_from_WeChat()【第四行】从文件获取数据
# log in WeChat
# bot = wxpy.Bot()
# group, wechat_data = read_data_from_WeChat(bot)


with open('group_data.json', 'r') as f:
    group, wechat_data = read_data_from_file(f)


# Initialize the plot
mpl.style.use('seaborn')
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
mpl.rcParams['xtick.labelsize'] = 16
mpl.rcParams['ytick.labelsize'] = 16
mpl.rcParams['legend.fontsize'] = 16
mpl.rcParams['axes.titlesize'] = 18
plt.rcParams.update({'font.size': 15})

# generate a figure
fig, axs = plt.subplots(3, 1, figsize=(9, 16))

# Process the sex_data
chat_data_of_sex = {int(k): v for k, v in wechat_data['sex'].items() if is_int(k)}
sex_num_dict = {'unknown': chat_data_of_sex[0], 'boy': chat_data_of_sex[1], 'girl': chat_data_of_sex[2]}
sex_data = {k: v for k, v in sex_num_dict.items() if v != 0}  # filter out the element which its value is 0

# show the sex_data as a pie
pie_title = "该群({0})的{1}比例".format(group.name, '性别')
get_pie(axs[0], sex_data, title=pie_title)
axs[0].title.set(y=1.1)  # Move the title up since it getting a little cramped

# Process the province_data (p:province)
p_bar_data = get_bar_data(wechat_data['province'], '省份')

# show the province_data as a bar
bar_title = "该群({0})的成员{1}分布".format(group.name, '省份')
get_a_bar(axs[1], p_bar_data, title=bar_title, if_sort=True)
axs[1].title.set(y=1.05)  # Move the title up since it getting a little cramped

# Process the city_data
c_bar_data = get_bar_data(wechat_data['city'], '城市')

# show the city_data as a bar
bar_title = "该群({0})的成员{1}分布".format(group.name, '城市')
get_a_bar(axs[2], c_bar_data, title=bar_title, if_sort=True)
axs[2].title.set(y=1.05)  # Move the title up since it getting a little cramped

# show the plot
fig.suptitle('群数据({0})'.format(group.name), fontsize=30)
# Adjust layout to prevent the overlap between bar's label and the next bar's title
fig.subplots_adjust(hspace=0.3)

fig.savefig('fig.pdf')
fig.show()
# bot.logout()
