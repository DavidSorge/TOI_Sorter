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


from time import time
import re
import os
from shutil import copy
import string
from winsound import Beep

#-------------------------------------------------------------------------------
# 1-4: Gets necessary metadata from xml file
#-------------------------------------------------------------------------------

def metadata_getter(xml_file_path):
    """Places publication date and headline from a given xml file in a library"""

    # Read file
    with open(xml_file_path) as input_file:
        raw_xml = input_file.read()

    # Extract Metadata
    file_metadata = {}
    # create a re.compile object that grabs the contents of RecordTitle, NumericPubDate and ObjectType tags.
    d = re.compile(r'<RecordTitle>(.*)</RecordTitle>|<NumericPubDate>(.*)</NumericPubDate>|<ObjectType>([^<]*)</ObjectType>*')
    # creates a list of tuples containing the intended tag strings
    metadata_matrix = d.findall(raw_xml)    

    # Assign entries to dictionary
    numeric_date = metadata_matrix[1][1]
    file_metadata["year"] = numeric_date[0:4]
    file_metadata["month"] = numeric_date[4:6]
    file_metadata["day"] = numeric_date[6:]
    file_metadata["headline"] = metadata_matrix[0][0][0:30]
    file_metadata["category"] = metadata_matrix[-1][-1]

    return file_metadata

#-------------------------------------------------------------------------------
# 5-7: Uses the metadata to file the xml file in a new data structure
#-------------------------------------------------------------------------------

def make_nested_directory(file_metadata):
    """
    Unless it already exists, creates directory
    \toi_archive_sorted\year\month\day\classification
    and returns the path of that directory.
    """

    file_metadata["category"] = file_metadata["category"].lower().translate(str.maketrans('','', string.punctuation))
    path_structure = ["year", "month", "day", "category"]
    directory = r"..\..\toi_archive_sorted"

    for layer in path_structure:
        directory = os.path.join(directory, file_metadata[layer])
        os.makedirs(directory, exist_ok=True)

    return directory

def sort_file(xml_file):
    """
    Saves a copy of an xml file in directory
    \toi_archive_sorted\year\month\day\classification
    naming it 'headline.xml'.
    """
    
    # Call earlier functions
    file_metadata = metadata_getter(xml_file)
    new_directory = make_nested_directory(file_metadata)
    
    # Construct Windows-compatible file name
    file_name = file_metadata["headline"].lower()
    file_name = file_name.translate(str.maketrans('','', string.punctuation))
    file_name = file_name.replace(" ","_")
    disalloweds = ["con", "prn", "aux", "nul", "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9"]
    if file_name in disalloweds:
        file_name = file_name + "1"
    else:
        pass
    file_name = file_name + ".xml"
    copy(xml_file, os.path.join(new_directory, file_name))

#-------------------------------------------------------------------------------
# 8: Applies the code above for all xmls in CWD's containing folder.
#-------------------------------------------------------------------------------



def get_folder_list():
    """
    Returns a list of the relative paths for all .xml files
    in relevant directory
    """
    
    return os.listdir(r'..\XML\18380101_20081231')
    
def list_xmls_in_folder(folder):
    """
    Returns a list of all the files in a folder
    """
    
    print("Now processing", folder)
    folder_path = os.path.join(r'..\XML\18380101_20081231', folder)
    file_list = os.listdir(folder_path)
    return file_list

def sort_all_xmls():
    """Sorts all xmls in the archive"""

    # Start timer and counter
    start_time = time()
    counter = 0

    # Sort files
    for folder in get_folder_list():
        files = list_xmls_in_folder(folder)
        for file in files:   
            counter += 1
            file = os.path.join(r'..\XML\18380101_20081231', folder, file)
            sort_file(file)
    
    # Give performance statistics and beep when done.
    elapsed = time() - start_time
    print(f"Sorted {counter} files in {elapsed} seconds")
    frequency = 2500
    duration = 500
    Beep(frequency, duration)
    
#-------------------------------------------------------------------------------
# 9: Checks whether all raw files correspond to one and only one sorted file
#-------------------------------------------------------------------------------


def compare(raw_path, sorted_path):
    """
    Check whether there are the same number of xml files in
    raw folder as there are in sorted folder.
    """
    
    # Generate Walk objects for the two directories
    raw_walk = os.walk(raw_path)
    sorted_walk = os.walk(sorted_path)

    # Generate a count of the number of files in each walk object
    raw_files = sum([len(files) for r, d, files in raw_walk])
    sorted_files = sum([len(files) for r, d, files in sorted_walk])

    # Tell user whether the number of files are the same or not
    print(f"there are {raw_files} files in the raw folder \n and {sorted_files} in the sorted folder")
    if raw_files == sorted_files:
        print("It worked!")
    else:
        print("Something went wrong; time to hunt for bugs!")


sort_all_xmls()

"""
# Test code: Only run after you think all files have been sorted.

raw path = r'..\XML'
sorted_path = r"..\..\toi_archive_sorted"
compare(raw_path, sorted_path)
"""