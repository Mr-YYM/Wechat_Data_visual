import wxpy
import re
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np


# implement a pie chart
def get_pie(a_plt, pie_data, category, labels=None):
    a_plt.clear()
    a_plt.axis("equal")
    a_plt.pie(pie_data, labels=labels, autopct='%1.1f%%')
    a_plt.set_title("该群({0})的{1}比例".format(group.name, category))


# implement a bar chart
def get_a_bar(a_plt, bar_data, category):
    a_plt.clear()
    a_plt.set_xlabel(category)
    a_plt.set_ylabel('数量')
    bar_names = list(bar_data.keys())
    bar_values = list(bar_data.values())
    a_plt.set_ylim(0, max(bar_values) + 25)
    a_plt.bar(range(len(bar_values)), bar_values, tick_label=bar_names)
    # set the text of value
    index = range(len(bar_values))
    for i, j in zip(index, bar_values):
        axs[1].text(i, j + 2, j, ha='center', va='bottom')
    a_plt.set_title("该群({0})的成员{1}分布".format(group.name, category))


def get_bar_data(p_data):
    fore_num, other_p_num, unknown_p_num = 0, 0, 0
    bar_data = {}
    staring_num = 0.1 * max(p_data.values())  # 单独成为一个柱体的条件: >= 0.1
    for k, v in p_data.items():
        if re.match('[\u4e00-\u9fa5]+',
                    k) is not None and v >= staring_num:  # China(in Chinese char) province and eligible
            bar_data[k] = v
        elif re.match('[\u4e00-\u9fa5]+', k) is not None:  # China(in Chinese char) province but ineligible
            other_p_num += v
        elif k == '':
            unknown_p_num += v
        else:
            fore_num += v  # foreign area
    bar_data["其他省份"] = other_p_num
    bar_data['国外'] = fore_num
    if unknown_p_num != 0:
        bar_data['unknown'] = unknown_p_num
    return bar_data


# initial the plot
mpl.style.use('seaborn')
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.rcParams.update({'font.size': 15})

# create a figure
fig, axs = plt.subplots(3, 1, figsize=(9, 10))

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

# Process the sex_data
gms_of_sex = group_members_stat['sex']
sex_num_dict = {'unknown': gms_of_sex[0], 'boy': gms_of_sex[1], 'girl': gms_of_sex[2]}
sex_data = list(sex_num_dict.values())
sex_labels = list(sex_num_dict.keys())

# generate a pie
get_pie(axs[0], sex_data, '性别', labels=sex_labels)

# Process the province_data (p:province)
p_bar_data = get_bar_data(group_members_stat['province'])

# show the province_data as a bar
get_a_bar(axs[1], p_bar_data, '省份')

# show the plot
fig.legend()
fig.suptitle('群数据')

fig.savefig('fig.png')
fig.show()
# bot.logout()
