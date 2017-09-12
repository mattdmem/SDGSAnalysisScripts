import argparse
from pybedtools import BedTool
import json
import requests

frequency = []

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
        r = requests.get("http://exac.hms.harvard.edu/rest/region/variants_in_region/"+query)

        alleles = []

        for allele in r.json():
            frequency.append(format(allele["allele_freq"],'f'))
            # line.append(json.dumps(allele,indent=4))
            if allele["allele_freq"] != 0.0:
                alleles.append(str(format(allele["allele_freq"],'f')) + "(" + str(allele["allele_count"]) + "/" + str(allele["allele_num"]) + ")")

        line.append(", ".join(alleles))

        print "\t".join(line)


    print max(frequency)


if __name__ == '__main__':
    main()