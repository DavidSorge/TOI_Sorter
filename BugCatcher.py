# -*- coding: utf-8 -*-
#
# Name:        TOI_Bug_Catcher
#-------------------------------------------------------------------------------
# Purpose:     Discover which recordIDs correspond to files uniquely in
#              either toi_archive_raw or toi_archive_sorted    
#
# Author:      David Sorge
#
# Created:     26/04/2019
# Copyright:   (c) David 2019
# Licence:     MIT Licence
#-------------------------------------------------------------------------------

"""
Overall specifications:
1: Gathers the record numbers of all the files in toi_archive_raw, and stores them to a list.
2: Opens each file in toi_archive_sorted, 
3: Extracts the <RecordID> tag
4: Removes that number from the l
5: If the number is not in the first set, adds it to a second set
6: Prints the numbers for any articles not found in the first 
"""

#-------------------------------------------------------------------------------
# 0: Imports
#-------------------------------------------------------------------------------

import os
from time import time

#-------------------------------------------------------------------------------
# 1: Definitions
#-------------------------------------------------------------------------------

class UniqueFileList:
    def __init__(self):
        self.raw = []
        self.sorted = []

def get_file_paths(folder):
    """
    For a given folder, generates the path for each file in the list
    """
    
    for root, dirs, files in os.walk(folder):
        for file in files:
            yield os.path.join(root, file)

def get_file_names(folder):
    """
    For a given folder, returns a dictionary with file name and path)
    """
    
    file_names = {}
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_names[file] = (os.path.join(root, file))
    return file_names

def record_id_extractor(file_paths):
    """
    For a given iterable list of file paths, extracts the RecordIDs from them
    """
    
    for file_path in file_paths:
        with open(file_path) as document:
            x = document.read(100)
            yield (x[-9:], file_path)


def find_uniques(raw_folder, sorted_folder): 
    """
    For a raw folder and a sorted folder, opens each file in the sorted folder,
    compares it to the list of files in the raw folder, and returns lists 
    of the unique files in each.
    """
    # Get list of record ids in the sorted folder
    sorted_file_paths = get_file_paths(sorted_folder)
    sorted_record_ids = record_id_extractor(sorted_file_paths)
    
    # Get list of file names in the raw folder
    raw_file_names = get_file_names(raw_folder)


    # If sorted id has a match, delete entry. If no match, add it to sorted unique list
    sorted_uniques = []
    raw_uniques = []
    for (record_id, path) in sorted_record_ids:
        file_name = record_id + ".xml"
        if file_name in raw_file_names.keys():
            del raw_file_names[file_name]
        else:
            sorted_uniques.append(path)
    
    # After removing all file names with matches, add the remaining to raw unique list
    for file_name in raw_file_names:
        raw_uniques.append(file_name)
        
    # Create an object consisting of two lists.
        unique_file_list = UniqueFileList()
        unique_file_list.sorted = sorted_uniques    
        unique_file_list.raw = raw_uniques
        

        unique_file_list.raw
    # return the pair of unique lists.
    return unique_file_list

#-------------------------------------------------------------------------------
# 2: Globals
#-------------------------------------------------------------------------------

start_time = time()
raw_folder = r"C:\Users\David\Documents\Research\toi-archive-subsample\XML"
sorted_folder = r"C:\Users\David\Documents\Research\toi_archive_sorted_test"

#-------------------------------------------------------------------------------
# 3: Calls
#-------------------------------------------------------------------------------

uniques = find_uniques(raw_folder, sorted_folder)


print("The following items are unique to the raw folder:")
print(uniques.raw)
print("The following items are unique to the sorted folder:")
print(uniques.sorted)
elapsed = (time()-start_time)
print(f"Completed in {elapsed:.2f} seconds")