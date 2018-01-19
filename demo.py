import wxpy
import re
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

# initial the plot
mpl.style.use('seaborn')
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号
plt.rcParams.update({'font.size': 15})

bot = wxpy.Bot()

# show and certify group
groups = bot.groups()
for k, v in enumerate(groups):
    print("%d、%s" % (k, v.name))
i = int(input("选定一个群"))
group = groups[i]

# get group info/data
group.update_group(True)
print(group.members.stats_text())
group_members_stat = group.members.stats()

# create a figure
fig, axs = plt.subplots(3, 1, figsize=(9, 10))
# Process the sex_data
sex_num = group_members_stat['sex']
boy, girl, unknown_sex = sex_num[1], sex_num[2], sex_num[0]
labels = ['boy', 'girl', 'unknown']
axs[0].axis("equal")
axs[0].pie([boy, girl, unknown_sex], labels=labels, autopct='%1.1f%%')
axs[0].set_title("该群({0})的性别比例".format(group.name))

# Process the province_data
p_datas = group_members_stat['province']
fore = 0
other_p = 0
unknown_p = 0
bar_datas = {}
for k, v in p_datas.items():
    if re.match('[\u4e00-\u9fa5]+', k) is not None and v >= 20:
        bar_datas[k] = v
    elif re.match('[\u4e00-\u9fa5]+', k) is not None:
        other_p += v
    elif k == '':
        unknown_p += v
    else:
        fore += v
bar_datas["其他省份"] = other_p
bar_datas['国外'] = fore
if unknown_p != 0:
    bar_datas['unknown'] = unknown_p


# show the province_data
axs[1].clear()
axs[1].set_xlabel('省份')
axs[1].set_ylabel('成员数量')

bar_names = list(bar_datas.keys())
bar_values = list(bar_datas.values())
axs[1].set_ylim(0, max(bar_values)+25)
axs[1].bar(range(len(bar_values)), bar_values, tick_label=bar_names)
# set the text of value
index = range(len(bar_values))
for i, j in zip(index, bar_values):
    axs[1].text(i, j+2, j, ha='center', va= 'bottom')

axs[1].set_title("该群({0})的成员省份分布".format(group.name))

# show the plot
fig.legend()
fig.suptitle('群数据')

fig.savefig('fig.png')
fig.show()
bot.logout()