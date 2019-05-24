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
from shutil import move
import string

#-------------------------------------------------------------------------------
# 1-4: Gets necessary metadata from xml file
#-------------------------------------------------------------------------------

def metadata_getter(xml_file_path):
    """Places publication date and headline from a given xml file in a library"""

    # Read file
    with open(xml_file_path, encoding = "utf8") as input_file:
        raw_xml = input_file.read()

    # Extract Metadata
    file_metadata = {}
    
    # create a re.compile object that grabs the contents of RecordTitle, NumericPubDate and ObjectType tags.
    d = re.compile(r'<RecordTitle>(.*)</RecordTitle>|<NumericPubDate>(.*)</NumericPubDate>|<ObjectType>([^<]*)</ObjectType>*')
    
    # creates a list of tuples containing the intended tag strings
    metadata_matrix = d.findall(raw_xml)    

    # Assign entries to dictionary
    try:
        numeric_date = metadata_matrix[1][1]
        file_metadata["year"] = numeric_date[0:4]
        file_metadata["month"] = numeric_date[4:6]
        file_metadata["day"] = numeric_date[6:]
        file_metadata["headline"] = metadata_matrix[0][0][0:30]
        file_metadata["category"] = metadata_matrix[-1][-1]
        
        return file_metadata
    
    except:
        print("Empty file detected:", xml_file_path)
        pass
        

#-------------------------------------------------------------------------------
# 5-7: Uses the metadata to file the xml file in a new data structure
#-------------------------------------------------------------------------------

def make_nested_directory(file_metadata, output_directory):
    """
    Unless it already exists, creates directory
    \toi_archive_sorted\year\month\day\classification
    and returns the path of that directory.
    """
    try:
        file_metadata["category"] = file_metadata["category"].lower().translate(str.maketrans('','', string.punctuation))
        path_structure = ["year", "month", "day", "category"]
        directory = output_directory
    
        for layer in path_structure:
            directory = os.path.join(directory, file_metadata[layer])
            os.makedirs(directory, exist_ok=True)
    
        return directory
    except:
        pass
    
def sort_file(xml_file_path, output_directory):
    """
    Saves a copy of an xml file in directory
    \toi_archive_sorted\year\month\day\classification
    naming it 'headline.xml'.
    """
    
    # Call earlier functions
    file_metadata = metadata_getter(xml_file_path)
    new_directory = make_nested_directory(file_metadata, output_directory)
    
    # Construct Windows-compatible file name
    try: 
        file_name = file_metadata["headline"].lower()
        file_name = file_name.translate(str.maketrans('','', string.punctuation))
        file_name = file_name.replace(" ","_")
        disalloweds = ["con", "prn", "aux", "nul", "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9", "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9"]
        if file_name in disalloweds:
            file_name = file_name + "1"
        else:
            pass
        file_name = file_name + ".xml"
        
        # Move the files to their new location
        move(xml_file_path, os.path.join(new_directory, file_name))
    except:
        pass
    
#-------------------------------------------------------------------------------
# 8: Applies the code above for all xmls in CWD's containing folder.
#-------------------------------------------------------------------------------

def sort_all_xmls(input_directory, output_directory):
    """Sorts all xmls in the archive"""

    # Start timer and counter
    start_time = time()
    counter = 0

    # Create a generator object for stuff in the input folder.
    files = os.scandir(input_directory)
    for file in files:   
        
        # Give me a running performance update
        if counter % 100 == 0:
            print(counter, "files processed...")
        else:
            pass
        
        # Generate the next file in the directory and apply the sort function
        counter += 1
        file_path = file.path
        sort_file(file_path, output_directory)


    
    # Give performance statistics and beep when done.
    elapsed = time() - start_time
    print(f"Sorted {counter} files in {elapsed} seconds")

#-------------------------------------------------------------------------------
# 10: Globals and Calls
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    input_directory = r'C:\Users\David\Documents\Research\toi-archive-subsample\XML'
    output_directory = r'C:\Users\David\Documents\Research\toi-archive-subsample\test2'
    sort_all_xmls(input_directory, output_directory)