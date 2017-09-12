from producers.StarLims import StarLimsApi
import sys

s = StarLimsApi()
sample_list = sys.argv[1]

count = 0
with open(sample_list) as f:
    for j in f:
        line=[]
        sample = j.rstrip()
        line.append(sample)
        result = s.ngs_by_container(sample)
        if "RunNumber" in result:
            if result["RunNumber"] != '1607514':
                line.append(result["RunNumber"])
            else:
                line.append("NA")
        else:
            line.append("FAIL")
        print ",".join(line)

count += 1
# if int(result["RunNumber"]) < 1607514:
#     print "warn"



print "count: " + str(count)

