import vcf
import seaborn as sns
import numpy as np
import scipy.stats as stats

in_both_count = 0
in_normal_count = 0
in_tumor_count = 0
af = []

vcf_reader = vcf.Reader(open('/sdgs/analysis/CLONEEXOME/somatic/P61_variants_normalised_decomposed_exac_cosmic_known_rare.vcf.gz', 'r'))
print "\t".join(["CHR","POS","REF","ALT","COSMIC","COSMIC COUNT","NORMAL DP","NORMAL AD","TUMOR DP","TUMOR AD","FISHERS","GENE","CDS","AA"])

# for record in vcf_reader:
#     if record.genotype("NORMAL")['GT'] == "0/1" or record.genotype("NORMAL")['GT'] == "1/1":
#         if record.genotype("TUMOR")['GT'] == "0/1" or record.genotype("TUMOR")['GT'] == "1/1":
#             in_both_count+=1
#     if record.genotype("TUMOR")['GT'] == "0/0":
#         print "hello"
#         print record
#         print record.genotype("NORMAL")
#         print record.genotype("TUMOR")
#         print record.INFO
#     if record.genotype("NORMAL")['GT'] == "0/0":
#         if record.genotype("TUMOR")['GT'] == "0/1" or record.genotype("TUMOR")['GT'] == "1/1":
#             normal_af = float(record.genotype("NORMAL")['FREQ'].replace("%", ""))
#             tumor_af = float(record.genotype("TUMOR")['FREQ'].replace("%",""))
#             af.append(tumor_af)
#
#
#             oddsratio, pvalue = stats.fisher_exact([[record.genotype("NORMAL")['AD'], record.genotype("NORMAL")['DP']], [record.genotype("TUMOR")['AD'], record.genotype("TUMOR")['DP']]])
#             if pvalue < 0.05:
#                 line = [record.CHROM,
#                         record.POS,
#                         record.REF,
#                         record.ALT[0],
#                         record.ID,
#                         record.INFO["CNT"],
#                         record.genotype("NORMAL")['DP'],
#                         record.genotype("NORMAL")['AD'],
#                         record.genotype("TUMOR")['DP'],
#                         record.genotype("TUMOR")['AD'],
#                         pvalue,
#                         record.INFO["GENE"],
#                         record.INFO["CDS"],
#                         record.INFO["AA"]]
#
#                 print "\t".join(str(x) for x in line)
#             elif record.genotype("NORMAL")['AD'] == 0:
#                 if record.genotype("TUMOR")['AD'] >= 5:
#                     line = [record.CHROM,
#                             record.POS,
#                             record.REF,
#                             record.ALT[0],
#                             record.ID,
#                             record.INFO["CNT"],
#                             record.genotype("NORMAL")['DP'],
#                             record.genotype("NORMAL")['AD'],
#                             record.genotype("TUMOR")['DP'],
#                             record.genotype("TUMOR")['AD'],
#                             pvalue,
#                             record.INFO["GENE"],
#                             record.INFO["CDS"],
#                             record.INFO["AA"]]
#
#                     print "\t".join(str(x) for x in line)
#
#
# sns.set_style('whitegrid')
# sns_plot = sns.kdeplot(np.array(af), bw=0.5)
# sns_plot.set(xlabel='Allele Frequency', ylabel='Density',title="Variants only in P61")
# fig = sns_plot.get_figure()
# fig.savefig("output.png")
#
# for record in vcf_reader:
#     if record.genotype("NORMAL")['GT'] == "0/1" or record.genotype("NORMAL")['GT'] == "1/1":
#         if record.genotype("TUMOR")['GT'] == "0/1" or record.genotype("TUMOR")['GT'] == "1/1":
#             in_both_count+=1
#     if record.genotype("TUMOR")['GT'] == "0/0":
#         pass
#         # print "hello"
#         # print record
#         # print record.genotype("NORMAL")
#         # print record.genotype("TUMOR")
#         # print record.INFO
#     if record.genotype("TUMOR")['GT'] == "0/0":
#         if record.genotype("NORMAL")['GT'] == "0/1" or record.genotype("NORMAL")['GT'] == "1/1":
#             normal_af = float(record.genotype("NORMAL")['FREQ'].replace("%", ""))
#             tumor_af = float(record.genotype("TUMOR")['FREQ'].replace("%",""))
#             af.append(normal_af)
#
#
#             oddsratio, pvalue = stats.fisher_exact([[record.genotype("TUMOR")['AD'], record.genotype("TUMOR")['DP']], [record.genotype("NORMAL")['AD'], record.genotype("NORMAL")['DP']]])
#             if pvalue < 0.05:
#                 line = [record.CHROM,
#                         record.POS,
#                         record.REF,
#                         record.ALT[0],
#                         record.ID,
#                         record.INFO["CNT"],
#                         record.genotype("NORMAL")['DP'],
#                         record.genotype("NORMAL")['AD'],
#                         record.genotype("TUMOR")['DP'],
#                         record.genotype("TUMOR")['AD'],
#                         pvalue,
#                         record.INFO["GENE"],
#                         record.INFO["CDS"],
#                         record.INFO["AA"]]
#
#                 print "\t".join(str(x) for x in line)
#             elif record.genotype("TUMOR")['AD'] == 0:
#                 if record.genotype("NORMAL")['AD'] >= 5:
#                     line = [record.CHROM,
#                             record.POS,
#                             record.REF,
#                             record.ALT[0],
#                             record.ID,
#                             record.INFO["CNT"],
#                             record.genotype("NORMAL")['DP'],
#                             record.genotype("NORMAL")['AD'],
#                             record.genotype("TUMOR")['DP'],
#                             record.genotype("TUMOR")['AD'],
#                             pvalue,
#                             record.INFO["GENE"],
#                             record.INFO["CDS"],
#                             record.INFO["AA"]]
#
#                     print "\t".join(str(x) for x in line)
#
#
# sns.set_style('whitegrid')
# sns_plot = sns.kdeplot(np.array(af), bw=0.5)
# sns_plot.set(xlabel='Allele Frequency', ylabel='Density',title="Variants only in P61")
# fig = sns_plot.get_figure()
# fig.savefig("output.png")
#
# for record in vcf_reader:
#     if record.genotype("NORMAL")['GT'] == "1/1" and record.genotype("TUMOR")['GT'] == "0/1":
#         oddsratio, pvalue = stats.fisher_exact([[record.genotype("TUMOR")['AD'], record.genotype("TUMOR")['DP']],
#                                                 [record.genotype("NORMAL")['AD'], record.genotype("NORMAL")['DP']]])
#         line = [record.CHROM,
#                 record.POS,
#                 record.REF,
#                 record.ALT[0],
#                 record.ID,
#                 record.INFO["CNT"],
#                 record.genotype("NORMAL")['DP'],
#                 record.genotype("NORMAL")['AD'],
#                 record.genotype("NORMAL")['GT'],
#                 record.genotype("TUMOR")['DP'],
#                 record.genotype("TUMOR")['AD'],
#                 record.genotype("TUMOR")['GT'],
#                 pvalue,
#                 record.INFO["GENE"],
#                 record.INFO["CDS"],
#                 record.INFO["AA"]]
#
#         print "\t".join(str(x) for x in line)

for record in vcf_reader:
    if record.genotype("NORMAL")['AD'] != 0:
        if float(record.genotype("TUMOR")['FREQ'].replace("%","")) < float(record.genotype("NORMAL")['FREQ'].replace("%","")):
            print record.CHROM+"\t"+str(record.genotype("NORMAL")['FREQ'].replace("%", ""))+"\t"+str(record.genotype("TUMOR")['FREQ'].replace("%",""))



