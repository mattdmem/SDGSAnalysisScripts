from helpers import FileParsers
import json
import argparse


def main():
    parser = argparse.ArgumentParser(description='compare two lists')
    parser.add_argument('--yourlist', metavar='yourlist', type=str, help='the path to sambamba depth regions file')
    parser.add_argument('--database', metavar='database', type=str, help='the path to the coverage summary json')


    args = parser.parse_args()

    database = []
    query = []
    with open(args.database, "r") as f:
        for line in f.readlines():
            database.append(line.rstrip())

        f.close()

    with open(args.yourlist, "r") as f:
        for line in f.readlines():
            query.append(line.rstrip())


    for i in query:
        if i in database:
            pass #print i + "FOUND"
        else:
            print i + " NOT FOUND"



if __name__ == '__main__':
    main()

