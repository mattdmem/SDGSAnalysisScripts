from producers.VariantProducers import VariantProducer
from models.Variants import *
import re
import csv

class horizon(VariantProducer):

    def __init__(self,file_name,sample,id_to_sample=None):
        self.file_name = file_name
        self.sample = sample
        self.id_to_sample = id_to_sample
        VariantProducer.__init__(self)

    def set_call_sets(self):
        sets = []
        if self.id_to_sample is not None:
            sample_name = self.id_to_sample[self.sample]
        else:
            sample_name = self.sample
        sets.append(CallSet(id=str(1), name=sample_name, sampleId=self.sample, variantSetIds=[self.variantSet.id]))
        return sets

    def set_variant_set(self):
        return VariantSet(metadata=[], id=str(0), datasetId=str(0))

    def add_to_info(self,field,data,infos):
        infos[field]=list()
        for i in data:
            infos[field].append(i)
        return infos

    def get_variants(self,bed=None):

        with open(self.file_name) as f:
            reader = csv.reader(f)
            for aline in reader:

                chrom = aline[1]
                pos = int(aline[2])
                ids = [aline[4].replace("\"","")]
                ref = aline[6]
                qual = 0
                alts = [aline[7]]
                format_values = ["GT","DP"]
                sample = ["0/1","0"]



                calls = []
                call = Call(callSetId=self.callSets[0].id, callSetName=self.callSets[0].name)
                for key, value in zip(format_values, sample):
                    if key == "GT":
                        if "./." in value:
                            call.genotype = []
                        elif "." in value:
                            value = value.replace(".", "").replace("/", "").replace("|", "")
                            call.genotype = [int(value)]
                        else:
                            call.genotype = map(int, re.split('/|\|', value))
                        if "|" in value:
                            call.phaseset = "phase"
                    elif key == "GL":
                        call.genotypeLikelihood = map(float, value.split(","))
                    else:
                        call.info[key] = value.split(",")
                calls.append(call)



                yield SDGSVariant(referenceName=chrom, filter=["PASS"], qual=0, referenceBases=ref, alternateBases=alts, names=ids, start=pos-1, end=pos-1+len(ref), calls=calls, id=chrom+"_"+str(pos)+"_"+ref, variantSetId=self.variantSet.id)

# print "##fileformat=VCFv4.1"
# print "##source=2016-03-31_MultiplexI_cfDNA_v2,genotypes and most other field faked"
# print "#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  HORIZON"

h = horizon(file_name='/home/bioinfo/2016-03-31_MultiplexI_cfDNA_v2.verified.csv',sample="HORIZON")
for i in h.get_variants():
    print i