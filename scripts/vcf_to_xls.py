import vcf
import json

out=[]



vcf_file = vcf.VCFReader(filename="/home/bioinfo/mparker/saudi_variants.recalibrated.filtered.all.snpeff.clinvar.modifier.vcf")
annotation_headers = vcf_file.infos["ANN"].desc
annotation_headers = annotation_headers.replace("Functional annotations: ","").replace("'","").replace(" ","")
annotation_fields = annotation_headers.split("|")

clnsig_header = vcf_file.infos["CLNSIG"].desc
clnsig_list = clnsig_header.replace("Variant Clinical Significance,","").replace(" ","").split(",")

clinsig_lookup = {}
for i in clnsig_list:
    code,description = i.split("-")
    clinsig_lookup[code]=description


clnevidence_header = vcf_file.infos["CLNREVSTAT"].desc
clnevidence_list = clnevidence_header.replace(" ","").split(",")

clnevidence_lookup = {}

samples = vcf_file.samples

header=["CHROM","POS","REF","ALT","DBSNP_ID","FILTER","QUAL"]
for sample in samples:
    header.append(sample)
header.append("CLINVAR")
header.append("GENE")
header.append("ANNOTATION")

out.append("\t".join(header))

for i in vcf_file:
    line=[]
    line.append(i.CHROM)
    line.append(str(i.POS))
    line.append(i.REF)
    alts=[]
    for j in i.ALT:
        alts.append(str(j))
    line.append(",".join(alts))
    if i.ID is None:
        line.append(".")
    else:
        line.append(i.ID)
    if len(i.FILTER) > 0:
        line.append(i.FILTER[0])
    else:
        line.append(".")
    line.append(str(i.QUAL))


    for sample in samples:
        line.append(i.genotype(sample)["GT"].replace("/","|"))

    clinvars = []
    if "CLNSIG" in i.INFO:
        clinvar = {}
        for count,j in enumerate(i.INFO["CLNHGVS"]):
            clinvar[j] = []
            for k in i.INFO["CLNSIG"][count].split("|"):
                clinvar[j].append(clinsig_lookup[k])
        clinvars.append(json.dumps(clinvar))
    line.append("|".join(clinvars))

    annotations=[]
    for j in i.INFO["ANN"]:
        annotation = {}
        anns = j.split("|")
        for count,field in enumerate(annotation_fields):
            annotation[field]=anns[count]
            if "Gene_ID" in annotation:
                gene=annotation["Gene_ID"]
            else:
                gene = ''
        annotations.append(json.dumps(annotation))
    line.append(gene)
    line.append("\t".join(annotations))

    out.append("\t".join(line))

target = open("/home/bioinfo/mparker/vcftoxls_low.tsv", 'w')
target.write("\n".join(out))
