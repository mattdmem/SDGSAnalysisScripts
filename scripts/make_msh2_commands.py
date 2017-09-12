from producers.StarLims import StarLimsApi
import argparse
import glob
import os
import subprocess


def run_command(cmd):
    try:
        subprocess.call(cmd, shell=True)
    except subprocess.CalledProcessError as e:
        print(cmd)
        print('Error executing command: ' + str(e.returncode))
        exit(1)


def get_fastq(run,container):
    fastq_list = glob.glob("/mnt/netapp1_archive/illumina/"+run+"/Data/Intensities/BaseCalls/*.fastq.gz")

    fastq_results = []
    for fastq in fastq_list:
        if container in fastq:
            fastq_results.append(fastq)

    return ",".join(sorted(fastq_results))

def get_command(container):
    s = StarLimsApi()

    info = s.ngs_by_container(container)

    if "MISEQ_RUN_NAME" not in info:
        print container+"\t"+"NOT_IN_API"
        exit()

    fastq = get_fastq(info["MISEQ_RUN_NAME"],container)


    broad = info["BED"]

    if not os.path.isfile("/results/Analysis/MiSeq/MasterBED/"+broad):

        broad = "/results/Analysis/MiSeq/MasterBED/archived_BED_files/"+broad
        if not os.path.isfile(broad):
            print container + "\t" + "NO_BROAD"+"\t"+broad
            exit()
    else:
        broad = "/results/Analysis/MiSeq/MasterBED/"+broad

    command = ['qsub',
               '-p -1023',
               '-o /results/Analysis/projects/MSH2_heredcancer_rerun/'+container+'.out',
               '-e /results/Analysis/projects/MSH2_heredcancer_rerun/' + container + '.err',
               '-N '+container,
               '/home/bioinfo/mparker/wc/hiseq_pipeline/sdgs_ngs_gene_panel_analysis.sh',
               fastq,
               info["RunNumber"]+"-"+container,
               "HeredCancer",
               info["CAPTUREMETHOD"],
               broad,
               "/results/Analysis/projects/MSH2_heredcancer_rerun/MSH2_exon5.bed",
               "/results/Analysis/MiSeq/MasterPolyList/ValidatedPolyLists/HeredCancer_polymorphism_list_v6.txt",
               info["AnalysisYear"],
               "MDP",
               "000",
               "/results/Analysis/MiSeq/MasterTranscripts/HeredCancer_preferred_transcripts.txt",
               "/results/Analysis/projects/MSH2_heredcancer_rerun/"+container,
               "False",
               "False"]

    #run_command(" ".join(command))

    bam = "/results/Analysis/projects/MSH2_heredcancer_rerun/"+container+"/"+info["RunNumber"]+"-"+container+"_Aligned_Sorted_Clipped_PCRDuped_IndelsRealigned.bam"
    #pileup= '/results/Pipeline/program/samtools-1.4/samtools view -h '+bam+' chr2:47641500-47641650 | /results/Pipeline/program/samtools-1.4/samtools mpileup --no-BAQ -vf /results/Pipeline/program/GATK_resource_bundle/ucsc.hg19.nohap.masked.fasta - | zcat - | grep 47641560'
    pileup = '/results/Pipeline/program/samtools-1.4/samtools view -h ' + bam + ' chr2:47641500-47641650 | /results/Pipeline/program/samtools-1.4/samtools mpileup --no-BAQ -f /results/Pipeline/program/GATK_resource_bundle/ucsc.hg19.nohap.masked.fasta - | grep 47641560'
    run_command(pileup)

def main():
    parser = argparse.ArgumentParser(description='runs pipeline for cell free DNA test')
    parser.add_argument('--container', metavar='sample', type=str, help='sample name')

    args = parser.parse_args()

    get_command(args.container)

if __name__ == '__main__':
    main()
