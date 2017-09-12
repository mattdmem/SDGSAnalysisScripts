#/rest/region/genes_in_region

import argparse
from pybedtools import BedTool
import json
import requests


def main():
    parser = argparse.ArgumentParser(description='check variants in region in genomeAD')
    parser.add_argument('--bed_file')
    args = parser.parse_args()

    regions = BedTool(args.bed_file)

    for region in regions:
        line = []
        line.append(str(region).rstrip())
        chrom = region.chrom.replace("chr","")
        query = "-".join([chrom,str(region.start),str(region.end)])
        r = requests.get("http://exac.hms.harvard.edu/rest/region/genes_in_region/"+query)

        genes = []
        for gene in r.json():
            print gene
            genes.append(gene["gene_name"])

        line.append(",".join(genes))

        print "\t".join(line)





if __name__ == '__main__':
    main()