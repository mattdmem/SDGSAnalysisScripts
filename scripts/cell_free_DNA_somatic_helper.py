from helpers import FileParsers
import argparse
import json
import subprocess
import os
from helpers.FileParsers import FileParser
from protocols.SDGSProtocols import *
import vcf
import numpy

software = {"samtools": "/sdgs/software/samtools-1.3.1/samtools",
            "bwa": "/sdgs/software/bwa-0.7.15/bwa",
            "picard": "/sdgs/software/picard-tools-2.5.0/picard.jar",
            "gatk": "/sdgs/software/GATK-3.6/GenomeAnalysisTK.jar",
            "varscan": "/sdgs/software/varscan/VarScan.v2.3.9.jar",
            "snpeff": "/sdgs/software/snpEff/snpEff.jar",
            "snpsift": "/sdgs/software/snpEff/SnpSift.jar",
            "bcftools": "/sdgs/software/bcftools-1.3.1/bcftools",
            "vt": "/sdgs/software/vt/vt",
            "sambamba": "/sdgs/software/sambamba_v0.6.3/sambamba"}
# resources = {"reference": "/sdgs/reference/ucsc.hg19.nohap.masked.fasta",
#              "dbsnp": "/sdgs/reference/dbsnp/common_all_20161122_GATK.vcf.gz",
#              "clinvar": "/sdgs/reference/clinvar/clinvar_20170130.vcf",
#              "bed": "/sdgs/analysis/bastock/Accel-Amplicon-EGFR-Pathway-chr.bed",
#              "bed_filled": "/sdgs/analysis/bastock/Accel-Amplicon-EGFR-Pathway-chr-FILLED.bed"}

resources = {"reference": "/sdgs/reference/ucsc.hg19.nohap.masked.fasta",
             "dbsnp": "/sdgs/reference/dbsnp/common_all_20161122_GATK.vcf.gz",
             "clinvar": "/sdgs/reference/clinvar/clinvar_20170130.vcf",
             "bed": "/sdgs/analysis/wells/HeredCancer_NF1_25_v1.bed",
             "bed_filled": "/sdgs/analysis/wells/HeredCancer_NF1_25_v1_filled.bed"}


def run_command(cmd):
    try:
        subprocess.call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(cmd)
        print('Error executing command: ' + str(e.returncode))
        exit(1)


def mapping(sample, out_dir, fastqs):
    out_file = out_dir + "/" + sample + ".bam"
    fastq = " ".join(fastqs)
    command = [software["bwa"], "mem", resources["reference"], "-t", "6",
               "-r \"@RG\\tID:" + sample + "\\tLB:" + sample + "\\tPL:illumina_HiSeq\\tSM:" + sample + "\\tPU:\"",
               fastq, "|", software["samtools"], "view", "-bhS", "-", "|", software["samtools"], "sort", "-", "-o",
               out_file]
    run_command(" ".join(command))

    return out_file


def add_rg(sample, bam, out_dir):
    out_file = out_dir + "/" + sample + "_rg.bam"
    command = ["java", "-XX:ParallelGCThreads=6", "-jar", software["picard"], "AddOrReplaceReadGroups", "INPUT=" + bam,
               "OUTPUT=" + out_file, "RGID=1", "RGLB=lib1", "RGPL=illumina", "RGPU=unit1", "RGSM=" + sample]
    print " ".join(command)
    run_command(" ".join(command))

    return out_file


def realign(sample, bam, out_dir):
    targets = out_dir + "/" + sample + ".realigntargets.intervals"

    command = [software["samtools"], "index", bam]
    run_command(" ".join(command))

    command = ["java", "-jar", software["gatk"], "-T", "RealignerTargetCreator", "-nt", "6", "-R",
               resources["reference"], "-dt", "NONE", "-I", bam, "", "-o", targets, "-L", resources["bed_filled"]]

    run_command(" ".join(command))

    out_file = out_dir + "/" + sample + "_rg_realigned.bam"
    command = ["java", "-jar", software["gatk"], "-T", "IndelRealigner", "-R",
               resources["reference"], "-I", bam, "-targetIntervals", targets, "-o", out_file,
               "--filter_mismatching_base_and_quals", "-L", resources["bed_filled"]]
    run_command(" ".join(command))

    return out_file


def bqsr(sample, bam, out_dir):
    bqsr_table = sample + "bqsr.table"
    command = ["java", "-jar", software["gatk"], "-T", "BaseRecalibrator", "-nct", "6", "-R", resources["reference"],
               "-I", bam, "-knownSites", resources["dbsnp"], "-o", bqsr_table]
    run_command(" ".join(command))

    out_file = out_dir + "/" + sample + "_rg_realigned_bqsr.bam"
    command = ["java", "-jar", software["gatk"], "-T", "PrintReads", "-nct", "6", "-R", resources["reference"], "-I",
               bam, "-BQSR", bqsr_table, "-o", out_file]
    run_command(" ".join(command))

    return out_file

def uniformity(sample,depth_bases,coverage_summary,out_dir):
    covs = []
    with open(depth_bases, "r") as f:
        for line in f:
            if line.startswith("chr"):
                ref, pos, cov, a, c, g, t, deletion, refskip, sample = line.rstrip().split("\t")
                covs.append(int(cov))

    point_2x = []
    point_5x = []
    onex = []
    one_point_5x =[]
    twox = []

    with open(coverage_summary) as data_file:
        data = json.load(data_file)
        c = CoverageSummary()
        coverage = c.fromJsonDict(data)
        print data
        print coverage

    total = len(covs)
    for cov in covs:
        if int(cov) > (float(coverage.mean) * 0.2):
            point_2x.append(cov)
        if int(cov) > (float(coverage.mean) * 0.5):
            point_5x.append(cov)
        if int(cov) > (float(coverage.mean) * 1.0):
            onex.append(cov)
        if int(cov) > (float(coverage.mean) * 1.5):
            one_point_5x.append(cov)
        if int(cov) > (float(coverage.mean) * 2.0):
            onex.append(cov)

    cv = coverage.sd / float(coverage.mean)
    u = Uniformity()

    prop_point_2x = (len(point_2x) / float(total)) * 100
    prop_point_5x = (len(point_5x) / float(total)) * 100
    prop_onex = (len(onex) / float(total)) * 100
    prop_1_point_5x_mean = (len(one_point_5x) / float(total)) * 100
    prop_twox = (len(twox) / float(total)) * 100

    u.prop_point_2x_mean = prop_point_2x
    u.prop_point_5x_mean = prop_point_5x
    u.prop_1x_mean = prop_onex
    u.prop_1_point_5x_mean = prop_1_point_5x_mean
    u.prop_2x_mean = prop_twox
    u.cv = cv

    validate = u.validate(u.toJsonDict())
    if validate:
        print u
        summary = out_dir + "/" + sample + "_coverage_uniformity.json"
        with open(summary, "wb") as f:
            f.write(json.dumps(u.toJsonDict(), indent=4))
            f.close()
    else:
        print "didn't validate coverage uniformity"

def coverage(sample, bam, out_dir):
    f = FileParser()

    out_file = out_dir + "/" + sample + "_depth_base.txt"
    command = [software["sambamba"], "depth", "base", "-o", out_file, "-c 0 -q 0 -L", resources["bed"], bam]
    run_command(" ".join(command))
    coverage_summary = f.parse_sambamda_depth_bases(out_file)

    print coverage_summary
    summary = out_dir + "/" + sample + "_coverage_summary.json"
    with open(summary, "wb") as f:
        f.write(json.dumps(coverage_summary.toJsonDict(), indent=4))
        f.close()

    f = FileParser()

    uniformity(sample,out_file,coverage_summary,out_dir)

    out_file = out_dir + "/" + sample + "_depth_region.txt"
    command = [software["sambamba"], "depth", "region","--cov-threshold=0","--cov-threshold=10","--cov-threshold=30","--cov-threshold=50","--cov-threshold=100","--cov-threshold=250","--cov-threshold=500","--cov-threshold=1000","-o", out_file, "-c 0 -q 0 -L", resources["bed"], bam]
    run_command(" ".join(command))

    print f.parse_sambamda_depth_regions(out_file)

    return summary


def alignment_stats(sample, bam, out_dir):
    # on target stats
    to_return = []

    out_file = out_dir + "/" + sample + ".ot_samtools_stats"
    command = [software["samtools"], "stats", "--ref-seq", resources["reference"], "-t", resources["bed"], bam,
               ">", out_file]
    run_command(" ".join(command))

    to_return.append(out_file)

    # all file stats
    out_file = out_dir + "/" + sample + ".all_samtools_stats"
    command = [software["samtools"], "stats", "--ref-seq", resources["reference"], bam, ">", out_file]
    run_command(" ".join(command))

    to_return.append(out_file)

    return to_return


def pileup(sample, bam, out_dir):
    out_file = out_dir + "/" + sample + ".mpileup"
    command = [software["samtools"], "mpileup", "--no-BAQ", "-f", resources["reference"], bam, ">", out_file]
    run_command(" ".join(command))

    return out_file


def call_variants(sample, tumor_pileup, normal_pileup, out_dir):
    out_file = out_dir + "/" + sample
    command = ["java", "-jar", software["varscan"], "somatic", normal_pileup, tumor_pileup, out_file, "--min-var-freq",
               "0.01", "--output-vcf", "1"]
    run_command(" ".join(command))

    out_vcf = out_dir + "/" + sample + "_variants.vcf"
    command = ["bgzip", out_file + ".snp.vcf"]
    run_command(" ".join(command))
    command = ["bgzip", out_file + ".indel.vcf"]
    run_command(" ".join(command))
    command = ["tabix", "-p", "vcf", out_file + ".snp.vcf.gz"]
    run_command(" ".join(command))
    command = ["tabix", "-p", "vcf", out_file + ".indel.vcf.gz"]
    run_command(" ".join(command))
    command = [software["bcftools"], "concat", "-a", out_file + ".snp.vcf.gz", out_file + ".indel.vcf.gz", "-o",
               out_vcf]
    run_command(" ".join(command))

    return out_vcf


def clean_variants(sample, vcf, out_dir):
    out_file = out_dir + "/" + sample + "_variants_normalised.vcf"
    command = [software["vt"], "normalize", vcf, "-r", resources["reference"], "-o", out_file]
    run_command(" ".join(command))
    out_vcf = out_dir + "/" + sample + "_variants_normalised_decomposed.vcf"
    command = [software["vt"], "decompose ", out_file, "-o", out_vcf]
    run_command(" ".join(command))

    return out_vcf


def annotate_variants(sample, vcf, out_dir):
    ann_out = out_dir + "/" + sample + "_variants_snpeff.vcf"
    command = ["java", "-jar", software["snpeff"], "ann", "hg19", vcf, ">", ann_out]
    run_command(" ".join(command))

    final_ann_out = out_dir + "/" + sample + "_variants_final.vcf"
    command = ["java", "-jar", software["snpsift"], "annotate", resources["clinvar"], ann_out, ">", final_ann_out]
    run_command(" ".join(command))

    return final_ann_out


def calculate_percent_on_target(sample, all_json, ot_json, out_dir):
    f = FileParser()

    samtools_all = f.parse_samtools(all_json, "all")

    samtools_ot = f.parse_samtools(ot_json, "rmdup")

    ot = (samtools_ot.reads_mapped_and_paired / float(samtools_all.reads_mapped_and_paired)) * 100

    with open(out_dir + "/" + sample + "_on_target.txt", "wb") as f:
        header = ["SAMPLE", "PERCENT_ON_TARGET"]
        f.write("\t".join(header) + "\n")
        line = [sample, str(ot)]
        f.write("\t".join(line) + "\n")
        f.close()

def estimate_tumor_in_normal_contamination(variants):
    # notes:
    # use frequencies in tumor and then in normal - has there been a reduction in allele frequency
    normal_freqs = []
    tumor_freqs = []
    status_list = []
    variant_dict = {}
    status = {0:"Reference",1:"Germline", 2:"Somatic", 3:"LOH", 5:"Unknown"}
    vcf_reader = vcf.Reader(open(variants, 'r'))
    for record in vcf_reader:
        id = record.CHROM+str(record.POS)+record.REF
        variant_dict[id]={}
        status_list.append(status[int(record.INFO["SS"])])
        variant_dict[id]["STATUS"] = status[int(record.INFO["SS"])]
        for sample in record.samples:
            # if "SOMATIC" not in record.INFO:
            if sample.sample == "NORMAL":
                variant_dict[id]["NORMAL_GT"]=sample["GT"]
                variant_dict[id]["NORMAL_FREQ"] = float(sample["FREQ"].replace("%",""))
                normal_freqs.append(float(sample["FREQ"].replace("%","")))
            if sample.sample == "TUMOR":
                variant_dict[id]["TUMOR_GT"] = sample["GT"]
                variant_dict[id]["TUMOR_FREQ"] = float(sample["FREQ"].replace("%",""))
                tumor_freqs.append(float(sample["FREQ"].replace("%","")))
    print normal_freqs
    print tumor_freqs
    print status_list
    print numpy.mean(normal_freqs)
    print numpy.mean(tumor_freqs)
    print json.dumps(variant_dict,indent=4)

    for v in variant_dict:
        if variant_dict[v]["TUMOR_FREQ"] > 5:
            if variant_dict[v]["TUMOR_FREQ"] > variant_dict[v]["NORMAL_FREQ"]:
                print variant_dict[v]["NORMAL_FREQ"]/float(variant_dict[v]["TUMOR_FREQ"])
                print variant_dict[v]

def find_true_germlines(sample, bam, out_dir):
    out_file = out_dir + "/" + sample + "_germline_variants.vcf"
    command = ["java","-jar",software["gatk"],"-T","HaplotypeCaller","-R",resources["reference"],"-I",bam,"--output_mode","EMIT_VARIANTS_ONLY","-o",out_file,"-L",resources["bed"],"-stand_call_conf","30","-stand_emit_conf","1" ]
    run_command(" ".join(command))

def main():
    parser = argparse.ArgumentParser(description='runs pipeline for cell free DNA test')
    parser.add_argument('--sample', metavar='sample', type=str, help='sample name')
    parser.add_argument('--fastqs_tumor', metavar='fastq_tumor', type=str, help='fastqs for the tumor')
    #arser.add_argument('--fastqs_normal', metavar='fastq_normal', type=str, help='fastq for the normal')
    parser.add_argument('--out_dir', metavar='out_dir', type=str, help='output directory')

    args = parser.parse_args()
    tumor = args.sample + "t"
    #normal = args.sample + "n"

    tumor_bam = mapping(tumor,args.out_dir,args.fastqs_tumor.split(","))
    #normal_bam = mapping(normal, args.out_dir, args.fastqs_normal.split(","))

    tumor_bam_rg = add_rg(tumor,tumor_bam,args.out_dir)
    #normal_bam_rg = add_rg(normal,normal_bam,args.out_dir)

    tumor_bam_rg_realign = realign(tumor,tumor_bam_rg,args.out_dir)
    #normal_bam_rg_realign = realign(normal, normal_bam_rg, args.out_dir)

    tumor_bam_rg_realign_bqsr = bqsr(tumor,tumor_bam_rg_realign,args.out_dir)
    #normal_bam_rg_realign_bqsr = bqsr(normal, normal_bam_rg_realign, args.out_dir)

    tumor_alignment_stats = alignment_stats(tumor,tumor_bam_rg_realign_bqsr,args.out_dir)
    #normal_alignment_stats = alignment_stats(normal, normal_bam_rg_realign_bqsr, args.out_dir)

    calculate_percent_on_target(tumor,tumor_alignment_stats[1],tumor_alignment_stats[0],args.out_dir)
    #calculate_percent_on_target(normal,normal_alignment_stats[1], normal_alignment_stats[0],args.out_dir)

    tumor_coverage = coverage(tumor, tumor_bam_rg_realign_bqsr, args.out_dir)
    #normal_coverage = coverage(normal, normal_bam_rg_realign_bqsr, args.out_dir)

    tumor_pileup = pileup(tumor,tumor_bam_rg_realign_bqsr,args.out_dir)
    #normal_pileup = pileup(normal,normal_bam_rg_realign_bqsr,args.out_dir)

    #variants = call_variants(args.sample,tumor_pileup,normal_pileup,args.out_dir)
    #clean_variant = clean_variants(args.sample,variants,args.out_dir)
    annotate = annotate_variants(args.sample,clean_variant,args.out_dir)

    #cov_uniformtiy = uniformity("135","/sdgs/analysis/bastock/testing_pipe/135t_depth_base.txt","/sdgs/analysis/bastock/testing_pipe/135t_coverage_summary.json","/sdgs/analysis/bastock/testing_pipe")

    # estimate_tumor_in_normal_contamination("/sdgs/analysis/bastock/testing_pipe/135variants_final.vcf")
    # find_true_germlines("135","/sdgs/analysis/bastock/testing_pipe/135n_rg_realigned_bqsr.bam","/sdgs/analysis/bastock/testing_pipe")

if __name__ == '__main__':
    main()
