from pygithub3 import Github
import time
from collections import OrderedDict
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from jinja2 import Environment, FileSystemLoader
from weasyprint import HTML
import inspect
import json
import time
import os
import numpy as np

def cm2inch(*tupl):
    inch = 2.54
    if isinstance(tupl[0], tuple):
        return tuple(i/inch for i in tupl[0])
    else:
        return tuple(i/inch for i in tupl)

auth = dict(login='mattdmem', password='')

start_year=2016
start_month=6

today=time.strftime("%d.%m.%y")

year=int(time.strftime("%Y"))
month=int(time.strftime("%m"))
day=int(time.strftime("%d"))

result=OrderedDict()

octocat_issues = gh.issues.list()
ids=[]

dates=[]
count=[]
open=[]
urgent=[]

issue=[]
user=[]

urgent_issue = []
urgent_user = []

open_issue = []
open_user = []

urgent_open_issue = []
urgent_open_user = []

if start_year == year:
    y = start_year
    prev_total = 0
    for m in reversed(range(start_month,month+1)):

        if m < 10:
            m = "0"+ str(m)
        total = 0
        open_total = 0
        urgent_total = 0
        date = str(y) + str(m) + "01"
        repo_issues_closed = gh.issues.list_by_repo('sch-sdgs', 'SDGSPipeline', state="closed",since=str(y) + str(m) + "01")
        for i in repo_issues_closed.iterator():
            if i.labels[0].name == "bug":
                if i.id not in ids:
                    print i.title
                    issue.append(i.title)
                    user.append(i.user.login)
                    print i.milestone
                    print i.user.login
                    ids.append(i.id)
                    total += 1

        repo_issues_open = gh.issues.list_by_repo('sch-sdgs', 'SDGSPipeline', state="open",
                                                  since=str(y) + str(m) + "01")

        for i in repo_issues_open.iterator():
            if i.labels[0].name == "bug":
                if i.id not in ids:
                    open_issue.append(i.title)
                    open_user.append(i.user.login)
                    ids.append(i.id)
                    open_total += 1

        repo_issues_urgent = gh.issues.list_by_repo('sch-sdgs', 'SDGSPipeline', state="closed",
                                                  since=str(y) + str(m) + "01")

        for i in repo_issues_urgent.iterator():
            if i.labels[0].name == "urgent":
                if i.id not in ids:
                    ids.append(i.id)
                    urgent_issue.append(i.title)
                    urgent_user.append(i.user.login)
                    urgent_total += 1

        repo_issues_urgent_open = gh.issues.list_by_repo('sch-sdgs', 'SDGSPipeline', state="open",
                                                    since=str(y) + str(m) + "01")

        for i in repo_issues_urgent_open.iterator():
            if i.labels[0].name == "urgent":
                if i.id not in ids:
                    ids.append(i.id)
                    urgent_open_issue.append(i.title)
                    urgent_open_user.append(i.user.login)
                    urgent_total += 1

        dates.append(date)
        count.append(total)
        open.append(open_total)
        urgent.append(urgent_total)
        result[date] = total

print count

rdates=list(reversed(dates))
rcount=list(reversed(count))
ropen=list(reversed(open))
rurgent=list(reversed(urgent))
y_pos = np.arange(len(rdates))
width = 0.35

from matplotlib import rcParams
rcParams.update({'figure.autolayout': True})

plt.figure(figsize=cm2inch(15, 10))
rects1=plt.bar(y_pos-2*(width/2), rcount, width, color='yellowgreen', align='center')
rects2=plt.bar(y_pos, ropen, width, color='lightcoral', align='center')
rects3=plt.bar(y_pos+2*(width/2), rurgent, width, color='gold', align='center')
print rects1
print rects2
print rects3
plt.legend((rects1[0], rects2[0], rects3[0]), ('Closed', 'Open', 'Urgent'),fontsize=8)
plt.xticks(y_pos, rdates,rotation=90,fontsize=9)
plt.yticks(fontsize=9)
plt.ylabel('Count', fontsize=9)
plt.title('Pipeline Bugs', fontsize=10)

image="/results/tmp/data.png"

plt.savefig(image)


plt.close()

test = pd.Series(user).value_counts()
closed_urgent_user_count = pd.Series(urgent_user).value_counts()
open_user_count = pd.Series(open_user).value_counts()

import matplotlib
matplotlib.style.use('ggplot')

plot=test.plot.pie(figsize=(2, 2),fontsize=6,colors=["yellowgreen","lightcoral","gold","lightskyblue"],shadow=True,labeldistance=0.2)
plot.yaxis.set_visible(False)
fig=plt.gcf()
image2="/results/tmp/data2.png"
fig.savefig(image2)

plt.close()

print closed_urgent_user_count
plot_closed_user_urgent=closed_urgent_user_count.plot.pie(figsize=(2, 2),fontsize=6,colors=["yellowgreen","lightcoral","gold","lightskyblue"],shadow=True,labeldistance=0.2)
plot_closed_user_urgent.yaxis.set_visible(False)
fig=plt.gcf()
image3="/results/tmp/data3.png"
fig.savefig(image3)

plt.close()

plot_open_user_count=open_user_count.plot.pie(figsize=(2, 2),fontsize=6,colors=["yellowgreen","lightcoral","gold","lightskyblue"],shadow=True,labeldistance=0.2)
plot_open_user_count.yaxis.set_visible(False)
fig=plt.gcf()
image4="/results/tmp/data4.png"
fig.savefig(image4)

plt.close()
if len(urgent_open_user) > 0:
    urgent_open_user_count = pd.Series(urgent_open_user).value_counts()

    plot_urgent_open_user_count=urgent_open_user_count.plot.pie(figsize=(2, 2),fontsize=6,colors=["yellowgreen","lightcoral","gold","lightskyblue"],shadow=True,labeldistance=0.2)
    plot_urgent_open_user_count.yaxis.set_visible(False)
    fig=plt.gcf()
    image5="/results/tmp/data5.png"
    fig.savefig(image5)

    plt.close()
else:
    image5="/results/tmp/blank.png"
env = Environment(loader=FileSystemLoader('.'))

table_issues = pd.DataFrame({"Issue":issue,"User": user})
urgent_issues = pd.DataFrame({"Issue":urgent_issue,"User": urgent_user})
open_issues = pd.DataFrame({"Issue":open_issue,"User": open_user})
urgent_open_issues = pd.DataFrame({"Issue":urgent_open_issue,"User":urgent_open_user})

template = env.get_template("resources/git_issues_report.html")

explain = "Two urgent bugs were reported in this period, one due to a bug in external software (SnpEff), which, when there are no variants in a patient no header is written to the VCF file.  The other was due to a change in file locations which prevented re-analysis running correctly. Both bugs were fixed and a new version of the pipeline validated and released"

template_vars = {"urgent_explanation":explain,"urgent_open_user":image5,"open_urgent":urgent_open_issues.to_html(classes=["table"],index=False,justify="left"),"open_user":image4,"closed_user_urgent":image3,"closed_user":image2,"open_issues":open_issues.to_html(classes=["table"],index=False,justify="left"),"today": today, "img": image,"issues":table_issues.to_html(classes=["table"],index=False,justify="left"),"urgent_issues":urgent_issues.to_html(classes=["table"],index=False,justify="left")}

html_out = template.render(template_vars)
HTML(string=html_out).write_pdf("/home/bioinfo/test.pdf",stylesheets=["resources/simple_report.css"])