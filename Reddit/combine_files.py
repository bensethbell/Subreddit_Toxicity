import pandas as pd
import numpy as np
import csv
import os
import sys

def get_file_names(path):
    all_files = os.listdir(path)
    comment_files = []
    sub_files = []
    for i in all_files:
        try:
            l = i.split('_')[1]
            if l[0] == 'c':
                comment_files.append(i)
            else:
                sub_files.append(i)
        except:
            print 'Error: ', i

    return comment_files, sub_files

def combine_files(file_list, filename):
    fout = open(filename, "a")
    for line in open(file_list[0]):
        fout.write(line)
    for i in file_list[1:]:
        f = open(i)
        f.next()
        for line in f:
            fout.write(line)
        f.close()
    fout.close()

if __name__ == '__main__':
    # comment_files_test, sub_files_test = get_file_names('/Users/Ben_Bell/Documents/Idibon/Subreddit_Toxicity/data')
    # comment_files_control, sub_files_control = get_file_names('/Users/Ben_Bell/Documents/Idibon/Subreddit_Toxicity/data_control')
    # comment_files_test = ['data/' + i for i in comment_files_test]
    # sub_files_test = ['data/' + i for i in sub_files_test]
    # comment_files_control = ['data_control/' + i for i in comment_files_control]
    # sub_files_control = ['data_control/' + i for i in sub_files_control]
    # combine_files(comment_files_test, 'comments_test.csv')
    # combine_files(sub_files_test, 'sub_test.csv')
    # combine_files(comment_files_control, 'comments_control.csv')
    # combine_files(sub_files_control, 'sub_control.csv')

    # combine_files(['comments_test.csv','comments_control.csv'], 'combined_comments.csv')

    # combine_files(['sub_test.csv','sub_control.csv'], 'combined_sub.csv')
    
    # comment_files_test, sub_files_test = get_file_names('/Users/loganduffy/Documents/Idibon/Subreddit_Toxicity/Reddit_Data/new_test0225/')
    comment_files_test, sub_files_test = get_file_names(os.getcwd())
    comment_files_test = [i for i in comment_files_test]
    sub_files_test = [i for i in sub_files_test]
    print 'comment_files_test', comment_files_test
    print 'sub_files_test', sub_files_test

    combine_files(comment_files_test, 'comments' + sys.argv[1] + '.csv')
    combine_files(sub_files_test, 'sub' + sys.argv[1] + '.csv')







