import argparse
import logging
import os
import json

def main():
    """
    a quick script to compare two lists of md5 sums in this format:

    ddc34f0996437fa20915756e9e9696db  ./incoming/illumina/170919_D00461_0184_BHVJCCBCXY/Thumbnail_Images/L002/C223.1/s_2_1204_G.jpg

    reports files missing from each list and also any md5sum issues
    dumps logging to output file specified and also logs a SUMMARY line that provides counts of mismatches etc
    these files are produced by running the following (on pinky)
    for i in `/home/pipeline/wc/SDGSAnalysisScripts/scripts/listdir |  grep ^file | /home/pipeline/wc/SDGSAnalysisScripts/scripts/get_random_line.sh`; do md5sum ${i}; done > file_integrity_check_netapp1

    """
    parser = argparse.ArgumentParser(description='compare two lists of md5sums and write the result to a file.')
    parser.add_argument('--master', metavar='master md5 file', type=str, help='file with md5 sum then the file path')
    parser.add_argument('--backup', metavar='backup md5 file', type=str, help='file with md5 sum then the file path')
    parser.add_argument('--output', metavar='full path to a file to log results', type=str, help='output log file for records')


    args = parser.parse_args()

    if os.path.isfile(args.output):
        print "FAIL: Output file exists - enter a non existent file!"
        exit()

    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)
    handler = logging.FileHandler(args.output)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    handler.setLevel(logging.INFO)
    logger.addHandler(handler)

    backup_results = {}

    summary = {}
    summary["total_files"] = 0
    summary["md5_fail"] = 0
    summary["missing_from_backup"] = 0
    summary["missing_from_master"] = 0

    with open(args.backup) as backup:
        for line in backup.readlines():
            md5,file = line.rstrip().split("  ")
            backup_results[file] = md5

            summary["total_files"]+=1

    with open(args.master) as master:
        for line in master.readlines():
            md5, file = line.rstrip().split("  ")
            if file in backup_results:
                if backup_results[file] != md5:
                    logger.critical(file)
                    logger.critical("MD5 DOESN'T MATCH")
                    summary["md5_fail"] += 1
                else:
                    logger.info(file)
                    logger.info("ok")
            else:
                logger.critical(file)
                logger.critical("FILE NOT FOUND IN BACKUP")
                summary["missing_from_backup"]+=1

    master_results = {}

    with open(args.master) as master:
        for line in master.readlines():
            md5, file = line.rstrip().split("  ")
            master_results[file] = md5

    with open(args.backup) as backup:
        for line in backup.readlines():
            md5, file = line.rstrip().split("  ")
            if file not in master_results:
                logger.critical(file)
                logger.critical("FILE NOT FOUND IN MASTER")
                summary["missing_from_master"] += 1


    logger.info("SUMMARY " + json.dumps(summary))

if __name__ == '__main__':
    main()

