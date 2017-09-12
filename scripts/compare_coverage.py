import os
import argparse
import glob
import json
from validation import misc_validation


def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f, 1):
            pass
    return i

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--worklist')

    old_version="v3_1"
    new_version="v3_1_1"

    args = parser.parse_args()

    samples = [x for x in os.listdir(args.worklist)]
    result = {}

    for i in samples:
        if os.path.isdir(args.worklist + "/" + i):
            if new_version not in i:
                sample=i.replace(old_version,"")
                result[sample] = {}
    groups=[]
    for i in samples:
        if os.path.isdir(args.worklist+"/"+i):
            if old_version in i:
                if new_version not in i:
                    sample=i.replace(old_version,"")
                    result[sample][old_version] = {}
                    bam=glob.glob(args.worklist+"/"+i+"/"+"*.bam")[0]
                    result[sample][old_version]["bam"] = bam

                    log = glob.glob(args.worklist+"/"+i+"/"+"*_analysis_log.txt")
                    with open(log[0]) as f:
                        for l in f:
                            if l.startswith("small-panel BED file"):
                                line = l.rstrip().split(" ")
                                bed = line[3]
                                result[sample][old_version]["bed"]=bed
                            if l.startswith("Disease group"):
                                line = l.rstrip().split(" ")
                                group = line [2]
                                result[sample]["group"] = group
                                if group not in groups:
                                    groups.append(group)
                            if l.startswith("Abbreviation for small panel"):
                                line=l.rstrip().split(" ")
                                abbrev = line[4]

                    variants = glob.glob(args.worklist + "/" + i + "/" + abbrev + "/" + "*LessLQsPolys.txt")[0]

                    result[sample][old_version]["variants"] = variants

                    old_gaps = glob.glob(args.worklist+"/"+i+"/"+abbrev+"/*_coverage_curve_30X.txt")
                    total_gaps_old = file_len(old_gaps[0]) - 1
                    min_file = glob.glob(args.worklist + "/" + i + "/" + abbrev + "/*MinCoverage.txt")
                    min=int()
                    max=int()
                    with open(min_file[0]) as f:
                        for l in f:
                            min = l.rstrip()
                    max_file = glob.glob(args.worklist + "/" + i + "/" + abbrev + "/*MaxCoverage.txt")
                    with open(max_file[0]) as f:
                        for l in f:
                            max = l.rstrip()

                    result[sample][old_version]["gaps"] = total_gaps_old
                    result[sample][old_version]["min"] = int(min)
                    result[sample][old_version]["max"] = int(max)

                else:
                    sample, version = i.split("v")
                    result[sample][new_version] = {}
                    bam = glob.glob(args.worklist + "/" + i + "/" + "*.bam")[0]
                    result[sample][new_version]["bam"] = bam

                    log = glob.glob(args.worklist + "/" + i + "/" + "*_analysis_log.txt")
                    with open(log[0]) as f:
                        for l in f:
                            if l.startswith("small-panel BED file"):
                                line = l.rstrip().split(" ")
                                bed = line[3]
                                result[sample][new_version]["bed"] = bed

                    folder = [x for x in os.listdir(args.worklist + "/" + i)]
                    for analysis_name in folder:
                        if os.path.isdir(args.worklist + "/" + i + "/" + analysis_name):
                            analysis_folder = os.path.basename(analysis_name)

                    variants = glob.glob(args.worklist + "/" + i + "/" + analysis_folder + "/" + "*LessLQsPolys.txt")[0]
                    result[sample][new_version]["variants"] = variants

                    new_gaps = glob.glob(args.worklist + "/" + i + "/" + analysis_folder + "/*_gaps_in_sequencing.txt")
                    if len(new_gaps) > 0:
                        total_gaps_new = file_len(new_gaps[0]) - 1
                    else:
                        total_gaps_new = "NA"

                    result[sample][new_version]["gaps"]=total_gaps_new

                    summary = glob.glob(args.worklist + "/" + i + "/" + analysis_folder + "/*_coverage_summary.txt")
                    if len(summary) > 0:
                        with open(summary[0]) as json_file:
                            json_data = json.load(json_file)
                            max = json_data["max"]
                            min = json_data["min"]
                    else:
                        max = "NA"
                        min = "NA"

                    result[sample][new_version]["min"] = min
                    result[sample][new_version]["max"] = max

    for sample in result:
        old=result[sample][old_version]
        new=result[sample][new_version]
        variant_validation = misc_validation.validate_variants(old["variants"], old["bam"], new["variants"], new["bam"], sample,"/results/Pipeline/masterBED_Backup/NGD_ataxia_150bp.bed")
        data = variant_validation["stats"].to_dict()
        shared = data["Variants Shared"][0]
        missing_old,x = data["Pass Variants Missing (All)"][0].split(" ")
        missing_new,x = data["Pass Variants Missing (All)"][1].split(" ")
        new["variants_missing"] = missing_new
        old["variants_missing"] = missing_old
        old["variants_shared"] = shared
        new["variants_shared"] = shared
        if new["max"] != "NA":
            max_diff=new["max"] - old["max"]
        else:
            max_diff="NA"
        if new["min"] != "NA":
            min_diff = new["min"] - old["min"]
        else:
            min_diff = "NA"
        if new["gaps"] != "NA":
            gaps_diff=new["gaps"] - old["gaps"]
        else:
            gaps_diff = "NA"

        result[sample]["max_diff"] = max_diff
        result[sample]["min_diff"] = min_diff
        result[sample]["gaps_diff"] = gaps_diff

        #do bedtools intersect to create a file that gives the new sites
        if gaps_diff > 0:
            pass


    for g in groups:


        header=["sample","disease_group","v3_bed","v3_1_bed","bed_status","v3_min","v3_1_min","min_diff","min_status","v3_max","v3_1_max","max_diff","v3_gaps","v3_1_gaps","gaps_diff","gap_status","shared_variants","missing_in_v3","missing_in_v3_1","variant_status\n"]

        file = open("/home/bioinfo/mparker/"+g+".csv",'w')

        file.write(",".join(header))


        for sample in result:

            group=result[sample]["group"]
            if group == g:
                v3_bed=result[sample]["v3.0"]["bed"]
                v3_1_bed = result[sample]["v3.1"]["bed"]
                v3_missing=result[sample]["v3.0"]["variants_missing"]
                v3_1_missing=result[sample]["v3.1"]["variants_missing"]
                shared=result[sample]["v3.0"]["variants_shared"]
                variant_status = "OK"
                if v3_1_missing > v3_missing:
                    variant_status = "CHECK"
                if v3_1_missing < v3_missing:
                    variant_status = "CHECK"
                bed_status = "OK"
                if v3_bed != v3_1_bed:
                    bed_status="BED_CHANGED"
                v3_min=result[sample]["v3.0"]["min"]
                v3_1_min=result[sample]["v3.1"]["min"]
                min_status = "OK"
                if v3_min >= 30:
                    if v3_1_min < 30:
                        min_status = "CHECK"
                v3_max = result[sample]["v3.0"]["max"]
                v3_1_max = result[sample]["v3.1"]["max"]
                v3_gaps = result[sample]["v3.0"]["gaps"]
                v3_1_gaps = result[sample]["v3.1"]["gaps"]
                max_diff = result[sample]["max_diff"]
                min_diff = result[sample]["min_diff"]
                gaps_diff = result[sample]["gaps_diff"]
                gap_status = "OK"
                if gaps_diff > 0:
                    gap_status = "CHECK"
                out = [sample,group,v3_bed,v3_1_bed,bed_status,v3_min,v3_1_min,min_diff,min_status,v3_max,v3_1_max,max_diff,v3_gaps,v3_1_gaps,gaps_diff,gap_status,shared,v3_missing,v3_1_missing,variant_status+"\n"]
                file.write(",".join(str(x) for x in out))
        file.close()
    #print json.dumps(result, indent=4)

if __name__ == '__main__':
    main()