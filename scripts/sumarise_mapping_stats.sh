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
flagstat=${i}/${worklist}-${sample}_Alignment.txt
offtarget=${i}/${worklist}-${sample}_ReadsOffTarget.txt

mapped=`grep "mapped (" $flagstat | cut -f1 -d" "`
percent=`grep "mapped (" $flagstat | cut -f5 -d" " | cut -f1 -d"%" | tr -d "("`
other=`head -1 $offtarget`

echo "$sample   $mapped $percent    $other"

done