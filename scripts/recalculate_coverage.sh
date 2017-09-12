#!/usr/bin/env bash

root=$1
worklist=$2

export PATH=${PATH}:/results/Pipeline/program/sambamba/build:/results/Pipeline/program/bedtools-2.17.0/bin

sample=`basename ${i}`

analysis_log=${i}/${worklist}-${sample}_analysis_log.txt
echo "ANALYSIS_LOG: $analysis_log"
bam_file=${i}/${worklist}-${sample}_Aligned_Clipped_Sorted_PCRDuped_IndelsRealigned.bam
bed_name=`grep "small-panel BED file" $analysis_log | grep -v "exonic" | head -1 | cut -f4 -d" "`
echo "BED_NAME: $bed_name"
bed_file=`find /results/Analysis/MiSeq/MasterBED -name "${bed_name}"`
echo "BED_FILE: $bed_file"
tmp=`mktemp -d`
echo $tmp
cd $tmp

grep -v "#" $bed_file > ${bed_name}.tmp

final_dir=`ls -d ${i}/*/ | head -1`
echo $final_dir

low_cov=`ls ${final_dir}${worklist}-${sample}_*_Alamut_coverage_curve_30X.bed`
old_low_cov=`basename $low_cov`

grep -v "chromosome" $low_cov > $old_low_cov

sambamba=/results/Pipeline/program/sambamba/build/sambamba
samtools=/results/Pipeline/program/samtools-1.3.1/samtools
gatk=/results/Pipeline/program/GenomeAnalysisTK-3.6/GenomeAnalysisTK.jar

#quality trim


#you have to remove the header line from the bed
bed_actual=`basename ${full_small_panel_bed}`
grep -v start ${full_small_panel_bed} > ${bed_actual}.temp.bed
exonic_bed_actual=`basename $exon_bed`
grep -v start ${exon_bed} > ${exonic_bed_actual}.temp.bed

# Generate coverage with sambamba (replaces bedtools part)
${sambamba} depth region \
    --cov-threshold=0 \
    --cov-threshold=10 \
    --cov-threshold=20 \
    --cov-threshold=30 \
    --cov-threshold=40 \
    --cov-threshold=50 \
    -q29 \
    -m \
    -L ${bed_actual}.temp.bed \
    ${worklist}-${sample}_Aligned_Clipped_Sorted_PCRDuped_IndelsRealigned.bam \
    > ${worklist}-${sample}_coverage_depth_regions_full_small_panel.txt

${sambamba} depth base \
    --min-coverage=0 \
    -q29 \
    -m \
    -L ${bed_actual}.temp.bed \
    ${worklist}-${sample}_Aligned_Clipped_Sorted_PCRDuped_IndelsRealigned.bam \
    > ${worklist}-${sample}_coverage_depth_bases_full_small_panel.txt.tmp

#fix problem with sambamba - basically find regions that are missing from bases file then fill them in with 0's

awk '{print($1"\t"$2"\t"$2+1"\t"$3)}' ${worklist}-${sample}_coverage_depth_bases_full_small_panel.txt.tmp | grep -v "COV" > ${worklist}-${sample}_coverage_depth_bases_full_small_panel.bed.tmp

/results/Pipeline/program/bedtools-2.17.0/bin/bedtools intersect -v -a ${bed_actual}.temp.bed -b ${worklist}-${sample}_coverage_depth_bases_full_small_panel.bed.tmp > regions_missing

while read i; do start=`echo "$i"|cut -f2`; end=`echo "$i"|cut -f3`; chr=`echo "$i"|cut -f1`; end_true=`echo "${end} - 1" | bc`; for j in $(seq $start $end_true);do new_end=`echo -e "${j} + 1" | bc`; echo -e "$chr\t${j}\t0\t0\t0\t0\t0\t0\t0\t${sample}" ;done ;done < regions_missing > to_add

cat ${worklist}-${sample}_coverage_depth_bases_full_small_panel.txt.tmp to_add > ${worklist}-${sample}_coverage_depth_bases_full_small_panel.txt

awk '{print($1"\t"$2"\t"$2+1"\t"$3)}' ${worklist}-${sample}_coverage_depth_bases_full_small_panel.txt > ${worklist}-${sample}_coverage_depth_bases_full_small_panel.bed

#################

# Generate coverage with sambamba (replaces bedtools part)
${sambamba} depth region \
    --cov-threshold=0 \
    --cov-threshold=10 \
    --cov-threshold=20 \
    --cov-threshold=30 \
    --cov-threshold=40 \
    --cov-threshold=50 \
    -m \
    -q29 \
    -L ${exonic_bed_actual}.temp.bed \
    ${worklist}-${sample}_Aligned_Clipped_Sorted_PCRDuped_IndelsRealigned.bam \
    > ${worklist}-${sample}_coverage_depth_regions_exonic.txt

${sambamba} depth base \
    --min-coverage=0 \
    -m \
    -q29 \
    -L ${exonic_bed_actual}.temp.bed \
    ${worklist}-${sample}_Aligned_Clipped_Sorted_PCRDuped_IndelsRealigned.bam \
    > ${worklist}-${sample}_coverage_depth_bases_exonic.txt.tmp


#fix problem with sambamba - basically find regions that are missing from bases file then fill them in with 0's

awk '{print($1"\t"$2"\t"$2+1"\t"$3)}' ${worklist}-${sample}_coverage_depth_bases_exonic.txt.tmp | grep -v "COV" > ${worklist}-${sample}_coverage_depth_bases_exonic.bed.tmp

/results/Pipeline/program/bedtools-2.17.0/bin/bedtools intersect -v -a ${exonic_bed_actual}.temp.bed -b ${worklist}-${sample}_coverage_depth_bases_exonic.bed.tmp > regions_missing

while read i; do start=`echo "$i"|cut -f2`; end=`echo "$i"|cut -f3`; chr=`echo "$i"|cut -f1`; end_true=`echo "${end} - 1" | bc`; for j in $(seq $start $end_true);do new_end=`echo -e "${j} + 1" | bc`; echo -e "$chr\t${j}\t0\t0\t0\t0\t0\t0\t0\t${sample}" ;done ;done < regions_missing > to_add

cat ${worklist}-${sample}_coverage_depth_bases_exonic.txt.tmp to_add > ${worklist}-${sample}_coverage_depth_bases_exonic.txt

awk '{print($1"\t"$2"\t"$2+1"\t"$3)}' ${worklist}-${sample}_coverage_depth_bases_exonic.txt > ${worklist}-${sample}_coverage_depth_bases_exonic.bed

##################

#get teh file that tehy use in alamut to show gaps that need filling
awk '{if($3 < 30) print $1"\t"$2"\t"$2+1"\t"$3}' ${worklist}-${sample}_coverage_depth_bases_exonic.txt  > ${worklist}-${sample}_bases_below_30x_exonic.bed

#intersect beds

/results/Pipeline/program/bedtools-2.17.0/bin/bedtools subtract -b ${exonic_bed_actual}.temp.bed -a ${bed_actual}.temp.bed > intronic.bed

# Generate coverage with sambamba (replaces bedtools part)
${sambamba} depth region \
    --cov-threshold=0 \
    --cov-threshold=10 \
    --cov-threshold=20 \
    --cov-threshold=30 \
    --cov-threshold=40 \
    --cov-threshold=50 \
    -m \
    -q29 \
    -L intronic.bed \
    ${worklist}-${sample}_Aligned_Clipped_Sorted_PCRDuped_IndelsRealigned.bam \
    > ${worklist}-${sample}_coverage_depth_regions_intronic.txt

${sambamba} depth base \
    --min-coverage=0 \
    -m \
    -q29 \
    -L intronic.bed \
    ${worklist}-${sample}_Aligned_Clipped_Sorted_PCRDuped_IndelsRealigned.bam \
    > ${worklist}-${sample}_coverage_depth_bases_intronic.txt.tmp


#fix problem with sambamba - basically find regions that are missing from bases file then fill them in with 0's

awk '{print($1"\t"$2"\t"$2+1"\t"$3)}' ${worklist}-${sample}_coverage_depth_bases_intronic.txt.tmp | grep -v "COV" > ${worklist}-${sample}_coverage_depth_bases_intronic.bed.tmp

/results/Pipeline/program/bedtools-2.17.0/bin/bedtools intersect -v -a intronic.bed -b ${worklist}-${sample}_coverage_depth_bases_intronic.bed.tmp > regions_missing

while read i; do start=`echo "$i"|cut -f2`; end=`echo "$i"|cut -f3`; chr=`echo "$i"|cut -f1`; end_true=`echo "${end} - 1" | bc`; for j in $(seq $start $end_true);do new_end=`echo -e "${j} + 1" | bc`; echo -e "$chr\t${j}\t0\t0\t0\t0\t0\t0\t0\t${sample}" ;done ;done < regions_missing > to_add

cat ${worklist}-${sample}_coverage_depth_bases_intronic.txt.tmp to_add > ${worklist}-${sample}_coverage_depth_bases_intronic.txt

awk '{print($1"\t"$2"\t"$2+1"\t"$3)}' ${worklist}-${sample}_coverage_depth_bases_intronic.txt > ${worklist}-${sample}_coverage_depth_bases_intronic.bed

#################

awk '{if($3 < 18) print $1"\t"$2"\t"$2+1"\t"$3}' ${worklist}-${sample}_coverage_depth_bases_intronic.txt  > ${worklist}-${sample}_bases_below_18x_intronic.bed

cat ${worklist}-${sample}_bases_below_30x_exonic.bed ${worklist}-${sample}_bases_below_18x_intronic.bed | /results/Pipeline/program/bedtools-2.17.0/bin/bedtools sort -i - > ${worklist}-${sample}_bases_not_covered.bed

/results/Pipeline/program/bedtools-2.17.0/bin/bedtools intersect -wb -a ${bed_actual}.temp.bed -b ${worklist}-${sample}_bases_not_covered.bed | cut -f1,2,4,8 | awk 'BEGIN{print "chromosome\tbp_pos\tregion\tdepth"}1' > ${worklist}-${sample}_${bed_abbrev}_gaps_in_sequencing.txt



 Generate samtools stats
${samtools} stats \
    -d \
    --ref-seq ${reference} \
    ${worklist}-${sample}_Aligned_Clipped_Sorted_PCRDuped_IndelsRealigned.bam \
    > ${worklist}-${sample}_samtools_stats_rmdup.txt

${samtools} stats \
    --ref-seq ${reference} \
    ${worklist}-${sample}_Aligned_Clipped_Sorted_PCRDuped_IndelsRealigned.bam \
    > ${worklist}-${sample}_samtools_stats_all.txt

/home/bioinfo/mparker/virtualenvs/sdgs/bin/python $script_dir/hiseq_v3.1_helper.py \
 --coverage ${worklist}-${sample}_coverage_depth_bases_full_small_panel.txt \
 --stats ${worklist}-${sample}_samtools_stats_all.txt \
 --stats_rmdup ${worklist}-${sample}_samtools_stats_rmdup.txt \
 --outputprefix ${worklist}-${sample}_${bed_abbrev}

#All bases coverage
#
#
#
#
#old_regions_count=`wc -l ${old_low_cov} | cut -f1 -d" "`
#
#if [ "$old_regions_count" -gt "0" ]
#then
##gives everything in the new calculation and asks if it's found in the old calculation - last column is 1 = yes 0 = no
#bedtools intersect -c -a ${worklist}-${sample}_bases_below_30x.bed -b $old_low_cov > ${worklist}-${sample}_overlaps_new.bed
#
#new_shared=`awk '{ SUM += $5} END { print SUM }' ${worklist}-${sample}_overlaps_new.bed`
#new_total=`wc -l ${worklist}-${sample}_overlaps_new.bed | cut -f1 -d" "`
#
##gives everything in old calculation and asks if it it's found in the new calculation
#bedtools intersect -c -b ${worklist}-${sample}_bases_below_30x.bed -a $old_low_cov > ${worklist}-${sample}_overlaps_old.bed
#
#old_shared=`awk '{ SUM += $5} END { print SUM }' ${worklist}-${sample}_overlaps_old.bed`
#old_total=`wc -l ${worklist}-${sample}_overlaps_old.bed | cut -f1 -d" "`
#
#else
#touch ${worklist}-${sample}_overlaps_new.bed
#new_shared=0
#new_total=`wc -l ${worklist}-${sample}_bases_below_30x.bed | cut -f1 -d" "`
#touch ${worklist}-${sample}_overlaps_old.bed
#old_shared=0
#old_total=0
#fi
#
#echo "new_method_shared new_method_total    old_method_shared   old_method_total" > ${worklist}-${sample}_coverage_assess.txt
#echo "$new_shared   $new_total  $old_shared $old_total" >> ${worklist}-${sample}_coverage_assess.txt
#
#cat ${worklist}-${sample}_coverage_assess.txt
##Region summaries
#
#sambamba depth region -q 30 -m --min-coverage=0 -T 0 -T 10 -T 20 -T 30 -T 40 -T 50 -L ${bed_name}.tmp $bam_file > ${worklist}-${sample}_region_summaries_coverage.txt
#
#mkdir -p ${final_dir}/new_coverage
#
#cp * ${final_dir}/new_coverage/
#

