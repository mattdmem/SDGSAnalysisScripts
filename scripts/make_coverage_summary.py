from helpers import FileParsers
import json
import argparse


def main():
    parser = argparse.ArgumentParser(description='calculate coverage uniformity')
    parser.add_argument('--bases', metavar='analysis_log', type=str, help='the path to sambamba depth regions file')
    parser.add_argument('--outfile', metavar='analysis_log', type=str, help='the path to the coverage summary json')


    args = parser.parse_args()

    f = FileParsers.FileParser()
    file = open(args.outfile, 'w')
    file.write(json.dumps(
        f.parse_sambamda_depth_bases(args.bases).toJsonDict(),
        indent=4))
    file.close()




if __name__ == '__main__':
    main()

