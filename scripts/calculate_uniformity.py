import json
from pprint import pprint
from protocols import SDGSProtocols
import argparse
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import gaussian_kde

def calculate_uniformity(regions,summary,dir,sample):
    coverage = SDGSProtocols.CoverageSummary()
    uniformtiy = SDGSProtocols.Uniformity()

    with open(summary) as data_file:
        data = json.load(data_file)

    c = coverage.fromJsonDict(data)

    try:
        f = open(regions)
    except IOError:
        msg = "FILE NOT FOUND: " + str(regions)
        raise Exception(msg)

    ok = []
    bad = []

    upper = c.mean + (c.mean * 0.2)
    lower = c.mean - (c.mean * 0.2)

    for line in f:
        if line.startswith("chr"):
            line = line.rstrip("\n")
            line = line.rstrip('\t')

            #chrom, start, end, name, readCount, meanCoverage, percentage0, percentage10, percentage20, percentage30, percentage40, percentage50, sample = line.split("\t")
            #chrom, start, end, name, readCount, meanCoverage, samplebed = line.split("\t")
            chrom, start, end, f3,f4,f5, readCount, meanCoverage, samplebed = line.split("\t")
            #chrom, start, end, readCount, meanCoverage, samplebed = line.split("\t")

            if lower <= float(meanCoverage) <= upper:
                ok.append(float(meanCoverage))
            else:
                bad.append(float(meanCoverage))


    uniformtiy = "{0:.2f}".format((len(ok) / float(len(ok) + len(bad)))*100)
    panel = summary.split("_")[1].split("/")[0]
    print sample+"\t"+panel+"\t"+str(uniformtiy)

    density = gaussian_kde(ok+bad)
    xs = np.linspace(0, max(ok+bad)+100, max(ok+bad)+100)
    density.covariance_factor = lambda: .25
    density._compute_covariance()
    plt.plot(xs, density(xs),color='black')
    plt.text(c.mean, 0.0001, uniformtiy+"%", fontsize=15)
    plt.axvline(x=c.mean,color='red')
    plt.axvline(x=upper,color='orange')
    plt.axvline(x=lower,color='orange')

    plt.savefig(dir+"/"+sample+'_uniformtiy.png')
    plt.show()





def main():
    parser = argparse.ArgumentParser(description='calculate coverage uniformity')
    parser.add_argument('--depth_regions', metavar='analysis_log', type=str, help='the path to sambamba depth regions file')
    parser.add_argument('--coverage_summary', metavar='analysis_log', type=str, help='the path to the coverage summary json')
    parser.add_argument('--sample', metavar='analysis_log', type=str,
                        help='sample name')
    parser.add_argument('--output_dir', metavar='analysis_log', type=str,
                        help='directory to output results')

    args = parser.parse_args()

    calculate_uniformity(args.depth_regions,args.coverage_summary,args.output_dir,args.sample)




if __name__ == '__main__':
    main()