#!/usr/bin/env bash

fastq_dir=$1
project_name=$2


source /home/dnamdp/virtualenvs/sdgs-matt/bin/activate

cd ${fastq_dir}

mkdir upload

cd upload

echo "compressing fastq files...."

tar -cvzf ${project_name}.tar.gz ${fastq_dir}/*.fastq.gz

echo " calculating md5sum...."

md5sum ${project_name}.tar.gz > ${project_name}.tar.gz.md5

echo "uploading files...."

aws s3 cp ${project_name}.tar.gz s3://sdgsdelivery/${project_name}/
aws s3 cp ${project_name}.tar.gz.md5 s3://sdgsdelivery/${project_name}/

echo "making urls...."

aws s3 presign s3://sdgsdelivery/${project_name}/${project_name}.tar.gz
aws s3 presign s3://sdgsdelivery/${project_name}/${project_name}.tar.gz.md5

