#!/usr/bin/env bash

#todo: re-write in python so that we can parse the json of barcodes to get sample names etc

export_directory=$1
vcfanno=/results/Pipeline/program/vcfanno/vcfanno
script_dir=/home/bioinfo/mparker/wc/hiseq_pipeline/scripts

dir=`mktemp -d`

echo ${dir}

counts=()
for i in `ls -d ${export_directory}/plugin_out/variantCaller_out.*`
do
    count=`basename ${i} | cut -f2 -d"."`
    counts+=("$count")
done

echo "${counts[@]}"
echo "${counts[*]}" | sort -nr | head -n1

for i in "${counts[@]}"; do
  (( i > max )) && max=$i
done

ls ${export_directory}/plugin_out/variantCaller_out.${max}/*.realigned.bam > ${dir}/bams.lst
ls ${export_directory}/plugin_out/variantCaller_out.${max}/IonXpress_*/TSVC_variants.vcf.gz > ${dir}/vcfs.lst

json=${export_directory}/plugin_out/variantCaller_out.${max}/barcodes.json

for i in `cat ${dir}/vcfs.lst`
do
    name=`echo ${i} | cut -f9 -d"/"`
    ${vcfanno} conf.toml ${i} > ${dir}/${name}.annotated.vcf
done

ls ${dir}/*.vcf > ${dir}/vcf_annotated.lst

python ${script_dir}/somatic_contamination.py --listofbams ${dir}/bams.lst --listofvcfs ${dir}/vcf_annotated.lst --output_type freq --output_dir ${dir}/