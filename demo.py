import wxpy
import re
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


# implement a pie chart
def get_pie(a_plt, pie_data, labels=None, title=None):
    a_plt.clear()
    a_plt.axis("equal")
    a_plt.pie(pie_data, labels=labels, autopct='%1.1f%%')
    a_plt.legend(loc='best')
    a_plt.set_title(title)


# implement a bar chart
def get_a_bar(a_plt, bar_data, category, title=None, if_sort=False):
    a_plt.clear()
    a_plt.set_xlabel(category)
    a_plt.set_ylabel('数量')
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
    staring_num = 0.1 * max(p_data.values())  # 单独成为一个柱体的条件: >= 0.1
    for k, v in p_data.items():
        if re.match('[\u4e00-\u9fa5]+',
                    k) is not None and v >= staring_num:  # China(in Chinese char) province and eligible
            bar_data[k] = v
        elif re.match('[\u4e00-\u9fa5]+', k) is not None:  # China(in Chinese char) province but ineligible
            other_num += v
        elif k == '':
            unknown_num += v
        else:
            fore_num += v  # foreign area
    bar_data["其他%s" % category] = other_num
    bar_data['国外'] = fore_num
    if unknown_num != 0:
        bar_data['unknown'] = unknown_num
    return bar_data


# log in WeChat
bot = wxpy.Bot()

# show and certify a group
groups = bot.groups()
for k, v in enumerate(groups):
    print("%d、%s" % (k, v.name))
s = int(input("选定一个群"))
group = groups[s]

# get group info/data
group.update_group(True)
print(group.members.stats_text())
group_members_stat = group.members.stats()

# initial the plot
mpl.style.use('seaborn')
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.rcParams.update({'font.size': 15})

# create a figure
fig, axs = plt.subplots(3, 1, figsize=(9, 16), dpi=200)

# Process the sex_data
gms_of_sex = group_members_stat['sex']
sex_num_dict = {'unknown': gms_of_sex[0], 'boy': gms_of_sex[1], 'girl': gms_of_sex[2]}
sex_data = list(sex_num_dict.values())
sex_labels = list(sex_num_dict.keys())

# show the sex_data as a pie
pie_title = "该群({0})的{1}比例".format(group.name, '性别')
get_pie(axs[0], sex_data, labels=sex_labels, title=pie_title)

# Process the province_data (p:province)
p_bar_data = get_bar_data(group_members_stat['province'], '省份')

# show the province_data as a bar
bar_title = "该群({0})的成员{1}分布".format(group.name, '省份')
get_a_bar(axs[1], p_bar_data, '省份', title=bar_title, if_sort=True)

# Process the city_data
c_bar_data = get_bar_data(group_members_stat['city'], '城市')

# show the city_data as a bar
bar_title = "该群({0})的成员{1}分布".format(group.name, '省份')
get_a_bar(axs[2], c_bar_data, '城市', title=bar_title)

# show the plot
fig.suptitle('群数据')

fig.savefig('fig.png')
fig.show()
# bot.logout()
