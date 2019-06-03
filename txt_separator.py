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
from shutil import rmtree

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

def xml_generator(zip_file_path):
    """
    For a given zip archive path, iteratively reads and yields in the contents 
    of each file in the zip archive.
    """
        
    #create ZipFile object, create list of files in ZipFile object
    with zipfile.ZipFile(zip_file_path, 'r') as active_zip_archive:
        files_list = active_zip_archive.namelist()
        
        #run get_raw_xml for each file in the archive
        for file_of_interest in files_list:
            xml_and_path = get_raw_xml(active_zip_archive, file_of_interest)
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
    xml_data["fulltext"] = parsed_xml.fulltext.string
    
    # Grab the original file location
    xml_data["zipped_loc"] = zipped_loc
    
    # Grab all objecttype tags and stick them in one field, separated by ;
    object_types = ''
    for type_tag in parsed_xml.find_all('objecttype'):
        if object_types == '':
            object_types = object_types + type_tag.string.lower()
        else:
            object_types = object_types + ';' + type_tag.string.lower()
    xml_data["objecttypes"] = object_types
    
    return xml_data

    
def write_txt(xml_data):
    """
    For a given library as constructed in get_data() above,
    creates a folder txt/year, writes a txt file in that folder
    containing the full text of the article,
    saves a copy of the pathname for the new file in the xml_data library
    (additionally saves a csv version of the pathname in xml_data library)
    """
    
    # Make the directory
    pub_year = xml_data["pub_date"]
    pub_year = pub_year[0:4]
    newpath = os.path.join('..', 'TXT', pub_year)
    if not os.path.exists(newpath):
        os.makedirs(newpath)
    
    # Compose the filepath
    file_name = xml_data["headline"].lower()
    file_name = file_name[0:51]
    file_name = file_name.translate(str.maketrans('','', punctuation))
    file_name = file_name.replace(" ","_")
    
    file_name = xml_data["record_id"] + file_name
    file_name_txt = file_name + '.txt'
    file_name_csv = file_name + '.csv'
    
    txtpath = os.path.join(newpath, file_name_txt)
    
    # Write the file
    with open(txtpath, 'w') as output_file:
        output_file.write(xml_data["fulltext"])
    
    # Add the path to the dictionary, return new dictionary
    xml_data["txt_path"] = txtpath
    xml_data["file_name_csv"] = file_name_csv
    return xml_data
    
def write_csv_row(xml_data):
    """
    Using an xml_data file as output by write_txt,
    writes a csv file with the content.
    """
    newpath = os.path.join('..', 'CSV')
    if not os.path.exists(newpath):
        os.mkdir(newpath)
    
    csvpath = os.path.join(newpath, xml_data['file_name_csv'])
    with open(csvpath, 'w', newline = '') as csvfile:
        fieldnames = ['record_id', 'headline', 'pub_date', 'start_page', 'url', 'zipped_loc', 'objecttypes', 'txt_path']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writerow({fn: xml_data[fn] for fn in fieldnames})

def concatenate_csvs(xml_data):
    with open('../TOI_metadata.csv', 'w', newline='') as single_file:
        
        # Write the header row
        fieldnames = ['record_id', 'headline', 'pub_date', 'start_page', 'url', 'zipped_loc', 'objecttypes', 'txt_path']
        writer = csv.DictWriter(single_file, fieldnames=fieldnames)
        writer.writeheader()
        
        # Concatenate the data
    with open('../TOI_metadata.csv', 'a') as single_file:
        files_list = os.listdir(os.path.join('..','CSV'))
        for file in files_list:
            with open(os.path.join('..', 'CSV', file), 'r') as in_file:
                for line in in_file:
                    single_file.write(line)
    rmtree(os.path.join('..', 'CSV'))
      
def process_all_zips(zip_files_path):
    """Find all zip files in a folder, add them to a list, and process all"""
    
    for zip_file_name in os.listdir(zip_files_path):
        print("Now processing:", zip_file_name)
        zip_file_path = os.path.join(zip_files_path, zip_file_name)
    
        for xml_and_path in xml_generator(zip_file_path):
            try:
                xml_data = get_data(xml_and_path)
                xml_data = write_txt(xml_data)
                write_csv_row(xml_data)
            except:
                pass
    concatenate_csvs(xml_data)
        
#-------------------------------------------------------------------------------
# Globals and Calls
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    
    #define which zip file to use REPLACE LATER WITH FOR-LOOP
    zip_files_path = os.path.join('..','ZIP')
    process_all_zips(zip_files_path)