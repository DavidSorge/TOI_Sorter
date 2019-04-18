# Name:        TOI_Sorter
#-------------------------------------------------------------------------------
# Purpose:     Sort input XML files by date and newspaper section
#
# Author:      David Sorge
#
# Created:     09/04/2019
# Copyright:   (c) David 2019
# Licence:     MIT Licence
#-------------------------------------------------------------------------------

"""
Overall specifications:
1:☺ Import an XML file from toi_archive_raw 
2:☺ Grab the year, month, and day of publication.
3:☺ Grab the Article Classification for the article.
4:☺ Grab the Headline for the Article
5:☺ Within toi_archive_sorted, create this nested folder structure:
     \toi_archive_sorted\year\month\day\classification
6:☺ Write a copy of that XML file into the appropriate folder
7:☺ (re)name the article with its headline
8:☺ Do this for all the xml files in containing folder's containing folder.
"""

#-------------------------------------------------------------------------------
# 0: Imports
#-------------------------------------------------------------------------------


import time
start_time = time.time()
import re
import os
from shutil import copy

#-------------------------------------------------------------------------------
# 1-4: Gets necessary metadata from xml file
#-------------------------------------------------------------------------------

def metadata_getter(xml_file_path):
    """Places publication date and headline from a given xml file in a library"""
    with open(xml_file_path) as input_file:
        raw_xml = input_file.read()
    file_metadata = {}
    d = re.compile(r'<RecordTitle>(.*)</RecordTitle>|<NumericPubDate>(.*)</NumericPubDate>|<ObjectType>([^<]*)</ObjectType>*') 
        # creates re.compile object that grabs the contents of RecordTitle, NumericPubDate and ObjectType tags.
    metadata_matrix = d.findall(raw_xml)    # creates a list of tuples containing the intended tag strings
    headline = metadata_matrix[0][0]    # grabs items from the tuples and puts them into a library
    numeric_date = metadata_matrix[1][1]
    category = metadata_matrix[-1][-1]
    file_metadata["year"] = numeric_date[0:4]
    file_metadata["month"] = numeric_date[4:6]
    file_metadata["day"] = numeric_date[6:]
    file_metadata["headline"] = headline
    file_metadata["category"] = category
    return file_metadata
    
#-------------------------------------------------------------------------------
# 5-7: Uses the metadata to file the xml file in a new data structure
#-------------------------------------------------------------------------------

def make_nested_directory(file_metadata):
    """Unless it already exists, creates directory
    \toi_archive_sorted\year\month\day\classification
    and returns the path of that directory."""
    file_metadata["category"] = file_metadata["category"].lower().replace(r"/",r"_").replace(" ","_")
    path_structure = ["year", "month", "day", "category"]
    directory = r"..\..\toi_archive_sorted"
    for layer in path_structure:
        directory = os.path.join(directory,file_metadata[layer])
        os.makedirs(directory, exist_ok=True)
    return directory

def sort_file(xml_file):
    """Saves a copy of an xml file in directory
    \toi_archive_sorted\year\month\day\classification
    naming it 'headline.xml'"""
    file_metadata = metadata_getter(xml_file)
    new_directory = make_nested_directory(file_metadata)
    file_name = file_metadata["headline"].lower()
    translation_table = file_name.maketrans("""<>:"/|?*""", """--------""")
    file_name.translate(translation_table).replace(" ","_") + ".xml"
    copy(xml_file, os.path.join(new_directory,file_name))

#-------------------------------------------------------------------------------
# 8: Implements the code above for all xmls in CWD's containing folder.
#-------------------------------------------------------------------------------

def get_xml_file_list():
    """Returns a list of the relative paths for all .xml files
    in current working directory and subdirectories"""
    file_list = []
    for root, dirs, files in os.walk('..'):
        for file in files:
            if file.endswith(".xml"):
                file_list.append(os.path.join(root,file))
    return file_list


def sort_all_xmls():
    """Sorts all xmls in the CWD's containing folder (recursive)"""
    files = get_xml_file_list()
    counter = 0
    for file in files:
        counter += 1
        sort_file(file)
    elapsed = time.time() - start_time
    print("Sorted {0} files in {1} seconds".format(counter, elapsed))

sort_all_xmls()
