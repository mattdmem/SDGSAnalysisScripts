import pybedtools
import pysam
from scipy import stats
import numpy as np


bed_file = "/results/Analysis/projects/iontorrent_read_quality/IEM_problem_region.designed"
bed = pybedtools.BedTool(bed_file)

bam = "/results/Analysis/Ion_Torrent/IEM/1701309/S1506832-02/1701309-S1506832-02.bam"
samfile = pysam.AlignmentFile("/results/Analysis/Ion_Torrent/IEM/1701309/S1506832-02/1701309-S1506832-02.bam", "rb" )



for region in bed:

    reverse_insertion_count = 0
    forward_insertion_count = 0
    tot_forward = 0
    tot_reverse = 0
    tot_bases_forward = 0
    tot_bases_reverse = 0
    for j in samfile.fetch(reference=str(region.chrom),start=int(region.start),end=int(region.end)):
        attributes = [attr for attr in dir(j)
                      if not attr.startswith('__')]

        read_length = j.inferred_length

        if j.flag == 16:
            tot_bases_reverse+=read_length
            tot_reverse+=1
            for i in j.cigarstring:
                if i == "I":
                    reverse_insertion_count+=1

        else:
            tot_bases_forward += read_length
            tot_forward += 1
            for i in j.cigarstring:
                if i == "I":
                    forward_insertion_count += 1



    # print str(forward_insertion_count) + "/" + str(tot_bases_forward)
    # print str(reverse_insertion_count) + "/" + str(tot_bases_reverse)
    #
    # print forward_insertion_count / float(tot_bases_forward)
    # print reverse_insertion_count / float(tot_bases_reverse)
    #
    # ratio_for = forward_insertion_count/float(tot_forward)
    # ratio_rev = reverse_insertion_count/float(tot_reverse)

    if reverse_insertion_count == 0:
        reverse_insertion_count = 0.00000000000000000000000000000000000000000000001

    ratio = (forward_insertion_count/float(tot_bases_forward))/(reverse_insertion_count/float(tot_bases_reverse))

    # obs = np.array([[tot_bases_forward-forward_insertion_count,forward_insertion_count],[tot_bases_reverse-reverse_insertion_count,reverse_insertion_count]])
    #
    # chi2, p, dof, expected = stats.chi2_contingency(obs,correction=True)
    #
    # print region.chrom+"\t"+str(region.start)+"\t"+str(region.end)+"\t"+str(p)+"\t"+str(ratio)

    print str(ratio)
