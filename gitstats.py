#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
'''Analyse git branch commit log, for every version, every person.
Usage:
gitstats -i <rootpath>
gitstats -h | --help
Options:
-h --help show this screen.
'''
import os
import re
import csv
import time
from docopt import docopt

GIT_LOG = "git -C \"{}\" log --since={} --until={} --pretty=tformat:%cn "\
           "--shortstat --no-merges --all > \"{}\""

REPATTERN_FULL = r"\s(\d+)\D+(\d+)\D+(\d+)\D+\n"
REPATTERN_INSERT_ONLY = r"\s(\d+)\D+(\d+)\sinsertion\D+\n"
REPATTERN_DELETE_ONLY = r"\s(\d+)\D+(\d+)\sdeletion\D+\n"

CSV_FILE_HEADER = ["library", "Author", "Commit", "Insert", "Delete", "Loc"]


def exec_git(repo, since, until, subdir):
    '''Execute git log commant, return string array.'''
    logfile = os.path.join(os.getcwd(), 'gitstats.txt')
    git_log_command = GIT_LOG.format(repo, since, until, logfile)
    print(repo)
    os.system(git_log_command)
    lines = None
    with open(logfile, 'r', encoding='utf-8') as logfilehandler:
        lines = logfilehandler.readlines()
    return lines


def save_csv(stats, csvfile):
    '''save stats data to csv file.'''
    try:
        with open(csvfile, 'w', encoding='utf-8', newline='') \
             as csvfilehandler:
            writer = csv.writer(csvfilehandler)
            writer.writerow(CSV_FILE_HEADER)
            for subitem in stats:
                for author, stat in subitem.items():
                    writer.writerow([stat[4], author, stat[0], stat[1],
                                     stat[2], stat[3]])
            csvfilehandler.close()
    except IOError as e:
        print("cannot open file:{0}, {1}".format(csvfile, str(e)))


def parse(libname, lines):
    '''Analyse git log and sort to csv file.'''
    prog_full = re.compile(REPATTERN_FULL)
    prog_insert_only = re.compile(REPATTERN_INSERT_ONLY)
    prog_delete_only = re.compile(REPATTERN_DELETE_ONLY)

    stats = {}
    for i in range(0, len(lines), 3):
        author = lines[i]
        # empty = lines[i+1]
        info = lines[i+2]
        # change = 0
        insert, delete = int(0), int(0)
        result = prog_full.search(info)
        if result:
            # change = result[0]
            insert = int(result.group(2))
            delete = int(result.group(3))
        else:
            result = prog_insert_only.search(info)
            if result:
                # change = result[0]
                insert = int(result.group(2))
                delete = int(0)
            else:
                result = prog_delete_only.search(info)
                if result:
                    # change = result[0]
                    insert = int(0)
                    delete = int(result.group(2))
                else:
                    print('Regular expression fail!')
                    return

        loc = insert - delete
        stat = stats.get(author)
        if stat is None:
            stats[author] = [1, insert, delete, loc, libname]
        else:
            stat[0] += 1
            stat[1] += insert
            stat[2] += delete
            stat[3] += loc
            stat[4] = libname

    return stats


def subdirlist(parentdir):
    """
    遍历主文件夹，获取当前目录下的子文件夹，不遍历子文件夹
    """
    subdirobjs = []
    list = os.listdir(parentdir)
    for line in list:
        filepath = os.path.join(parentdir, line)
        if os.path.isdir(filepath):
            subdirobjs.append(filepath)

    return subdirobjs


if __name__ == "__main__":
    print('gitstats begin')
    arguments = docopt(__doc__, version='Naval Fate 2.0')
    rootpath = arguments['<rootpath>']
    if len(arguments['<rootpath>']) == 0:
        print('Invalid argv parameters.')
        exit(0)
    '''
    if len(sys.argv) != 2:
        print('Invalid argv parameters.')
        exit(0)
    '''
    curtime = time.strftime("%Y-%m-%d", time.localtime())
    csvname = "Statistics_" + curtime + ".csv"
    # CSV_FILE = os.path.join(os.getcwd(), csvname)
    CSV_FILE = "D:/Shared/研发/gitstats/" + csvname
    outdic = []
    REPO = os.path.join(os.getcwd(), rootpath)
    # print(REPO)
    objslist = subdirlist(REPO)
    assert objslist is not None
    for item in objslist:
        # print("sub directory: " + item)
        if item.find('.git') >= 0:
            continue
        SINCE = "1.week"  # sys.argv[2]
        UNTIL = "now"  # sys.argv[3]
        # CSV_FILE = os.path.join(item, "test.csv")
        LINES = exec_git(item, SINCE, UNTIL, item)
        assert LINES is not None
        pos = item.rfind('\\') + 1
        libitem = item[pos:]
        STATS = parse(libitem, LINES)
        outdic.append(STATS)
    '''
    SUB_DIR = sys.argv[4]
    CSV_FILE = os.path.join(os.getcwd(), sys.argv[5])
    '''
    save_csv(outdic, CSV_FILE)
    print('gitstats done')
