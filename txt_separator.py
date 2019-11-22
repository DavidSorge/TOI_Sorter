# -*- coding: utf-8 -*-
"""
Created on Fri May 31 16:15:05 2019

@author: David
"""

#-------------------------------------------------------------------------------
# Specifications
#-------------------------------------------------------------------------------
"""
    1: Start with the raw archive in ZIP format
    2: For each XML file in the ZIP archive:
        3: Write a line in a csv file with the metadata for that file.
        4: Create a folder with the publication year for that file
        5: Write a text file with the article's fulltext
"""


#-------------------------------------------------------------------------------
# Imports
#-------------------------------------------------------------------------------

import zipfile
import bs4
import os
from string import punctuation
import csv
import pandas

#-------------------------------------------------------------------------------
# Definitions
#-------------------------------------------------------------------------------

def get_raw_xml(active_zip_archive, file_of_interest):
    """
    For a file of interest in an active zip archive,
    returns the raw xml as a string.
    """
    
    with active_zip_archive.open(file_of_interest, 'r') as file:
        raw_xml = file.read()
        zip_path = active_zip_archive.filename
    return (raw_xml, zip_path, file_of_interest)

def xml_generator(zip_file_path, df):
    """
    For a given zip archive path, iteratively reads and yields in the contents 
    of each file in the zip archive.
    """
        
    #create ZipFile object, create list of files in ZipFile object
    with zipfile.ZipFile(zip_file_path, 'r') as active_zip_archive:
        files_list = active_zip_archive.namelist()
        
        #run get_raw_xml for each file in the archive
        for file_of_interest in files_list:
            if is_processed(file_of_interest, df):
                pass
            else:
                xml_and_path = get_raw_xml(active_zip_archive, file_of_interest)
                yield xml_and_path

def xml_generator_unzipped(xml_folder_path):
	"""
	For a given folder with unzipped XML files, iteratively reads and yields in
	the contents of each file.
	"""
    for root, dirs, files in os.walk(xml_folder_path):
        for name in files:
            zip_path = ''
            file_of_interest = name            
            print("Processing:", file_of_interest)
            with open(os.path.join(root, name), 'r') as input_file:
                raw_xml = input_file.read()
            xml_and_path = (raw_xml, zip_path, file_of_interest)
            yield xml_and_path

def get_data(xml_and_path):
    """
    From the raw text of an xml file, creates a library with relevant metadata
    and file text.
    """
    # Prep: create/reset library, parse xml
    xml_data = {}
    raw_xml = xml_and_path[0]
    zipped_loc = os.path.join(xml_and_path[1], xml_and_path[2])
    parsed_xml = bs4.BeautifulSoup(raw_xml, "lxml")
   
    # Grab the straightforward data from the xml and stick them in the library
    xml_data["record_id"] = parsed_xml.recordid.string
    xml_data["headline"] = parsed_xml.recordtitle.string
    xml_data["pub_date"] = parsed_xml.numericpubdate.string
    xml_data["start_page"] = parsed_xml.startpage.string
    xml_data["url"] = parsed_xml.urldocview.string

    # Grab all objecttype tags and stick them in one field, separated by ;
    object_types = ''
    for type_tag in parsed_xml.find_all('objecttype'):
        if object_types == '':
            object_types = object_types + type_tag.string.lower()
        else:
            object_types = object_types + ';' + type_tag.string.lower()
    xml_data["objecttypes"] = object_types

    # Grab the full text and story it in the library
    try:
        xml_data["fulltext"] = parsed_xml.fulltext.string
        xml_data["note"] = ''
    except:
        print(xml_data["record_id"], "has no text. It is a", xml_data["objecttypes"])
        xml_data["fulltext"] = "No Text"
        xml_data["note"] = 'No text'
    
    # Grab the original file location
    xml_data["zipped_xml_loc"] = zipped_loc
        
    return xml_data

    
def write_txt(xml_data):
    """
    For a given library as constructed in get_data() above,
    creates a folder txt/year, writes a txt file in that folder
    containing the full text of the article,
    saves a copy of the pathname for the new file in the xml_data library
    (additionally saves a csv version of the pathname in xml_data library)
    """
    
    # Make TXT directory
    if not os.path.exists(r'../TXT'):
        os.mkdir(r'../TXT')
    
    # Compose the archive name
    pub_year = xml_data["pub_date"]
    pub_year = pub_year[0:4]
    
    
    # Make archive path
    zip_path = os.path.join(r'../TXT', pub_year + '.zip')
    
    # Compose the file name
    file_name = xml_data["headline"].lower()
    file_name = file_name[0:51]
    file_name = file_name.translate(str.maketrans('','', punctuation))
    file_name = file_name.replace(" ","_")
    file_name = xml_data["record_id"] + file_name + '.txt'
    
    fulltext = xml_data["fulltext"]
    
    # Create the archive, and write the txt file in the archive
    with zipfile.ZipFile(zip_path, 'a') as output_archive:
        output_archive.writestr(file_name, fulltext) 
            
        
        
    # Add the path to the dictionary, return new dictionary
    xml_data["txt_zip"] = zip_path
    xml_data["txt_file"] = file_name
    
    return xml_data

def write_header_row(xml_data):
    """
    writes a header row for the TOI_metadata file
    """
    
    with open(r'../TOI_metadata.csv', 'w', newline='') as single_file:
        
        # Write the header row
        fieldnames = ['record_id', 'headline', 'pub_date', 'start_page', 'url', 'zipped_xml_loc', 'txt_zip', 'txt_file', 'note', 'objecttypes']
        writer = csv.DictWriter(single_file, fieldnames=fieldnames)
        writer.writeheader()

def write_csv_row(xml_data):
    """
    Using an xml_data file as output by write_txt,
    writes a line in the TOI_metadata file containing the relevant fieldnames
    """    
    
    csvpath = r'../TOI_metadata.csv'
    with open(csvpath, 'a', newline = '') as csvfile:
        fieldnames = ['record_id', 'headline', 'pub_date', 'start_page', 'url', 'zipped_xml_loc', 'txt_zip', 'txt_file', 'note', 'objecttypes']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({fn: xml_data[fn] for fn in fieldnames})

def process_all_zips(zip_files_path, df):
    """Find all zip files in a folder, add them to a list, and process all"""
    
    firsttime = True
    for zip_file_name in os.listdir(zip_files_path):
        print("Now processing:", zip_file_name)
        zip_file_path = os.path.join(zip_files_path, zip_file_name)
        
        for xml_and_path in xml_generator(zip_file_path, df):
            xml_data = get_data(xml_and_path)
            xml_data = write_txt(xml_data)
            if firsttime:
                write_header_row(xml_data)
                firsttime = False
            else:
                pass
            write_csv_row(xml_data)
            
def process_all_xmls(xml_folder_path):
    firsttime = True
    for xml_and_path in xml_generator_unzipped(xml_folder_path):
        xml_data = get_data(xml_and_path)
        xml_data = write_txt(xml_data)
        if firsttime:
            write_header_row(xml_data)
            firsttime = False
        else:
            pass
        write_csv_row(xml_data)

# These bits need testing, and will eventually need to be integrated into functions above.

def load_completed_ids():
    """
    Open the TOI_metadata csv file created by an interrupted version
    of this script, return a dataframe containing the record_ids of xml files
    already processed.
    """

    csvpath = r'../TOI_metadata.csv'
    if os.path.exists(csvpath):
        df = pandas.read_csv(csvpath, usecols=['record_id'])
    else:
        df = pandas.DataFrame()
        df['record_id'] = ''
    return df

def is_processed(xml_file, df):
    """
    For a given xml_file, use the file name to check whether the file has a 
    corresponding entry in the input dataframe.
    """
    file_name_id = os.path.splitext(xml_file)[0]
    is_processed = df.isin([file_name_id]).any().values[0]
    return is_processed
        
#-------------------------------------------------------------------------------
# Globals and Calls
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    """
    df = load_completed_ids()
    zip_files_path = r'../ZIP'
    process_all_zips(zip_files_path, df)
    """
    xml_folder_path = r'../XML'
    process_all_xmls(xml_folder_path)