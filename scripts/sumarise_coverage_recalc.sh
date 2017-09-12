#!/usr/bin/env bash

worklist=$1
year=$3
machine=$2

export PATH=${PATH}:/results/Pipeline/program/sambamba/build:/results/Pipeline/program/bedtools-2.17.0/bin


if [ "$machine" == "hiseq" ]
then
root=/results/Analysis/HiSeq/${year}/${worklist}/*/

elif [ "$machine" == "miseq" ]
then

root=/results/Analysis/MiSeq/Runs/${year}/${worklist}/*/

fi

for i in `ls -d ${root}`
do
sample=`basename ${i}`
analysis_log=${i}/${worklist}-${sample}_analysis_log.txt
bam_file=${i}/${worklist}-${sample}_Aligned_Sorted_PCRDuped_IndelsRealigned.bam
bed_name=`grep "small-panel BED file" $analysis_log | grep -v "exonic" | head -1 | cut -f4 -d" "`
bed_file=`find /results/Analysis/MiSeq/MasterBED -name "${bed_name}"`

coverage_file=`ls ${i}/*/new_coverage/${worklist}-${sample}_coverage_assess.txt`

values=`grep -v new $coverage_file`

echo "$sample   $bed_name   $values"

done