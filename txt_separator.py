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
    return raw_xml

def xml_generator(zip_file_path):
        #create ZipFile object, create list of files in ZipFile object
    with zipfile.ZipFile(zip_file_path, 'r') as active_zip_archive:
        files_list = active_zip_archive.namelist()
        for file_of_interest in files_list:
            raw_xml = get_raw_xml(active_zip_archive, file_of_interest)
            yield raw_xml


def get_data(raw_xml):
    """
    From the raw text of an xml file, creates a library with relevant metadata
    and file text.
    Gets the following:
        1: <RecordID>
        2: <RecordTitle>
        3: <NumericPubDate>
        4: <ObjectType> tags (all)
        5: <StartPage>
        6: <URLDocView>
        7: <FullText>
    """
    xml_data = {}
    parsed_xml = bs4.BeautifulSoup(raw_xml, "lxml")
    
    xml_data["record_id"] = parsed_xml.find_all("recordid")[0].gettext()
    xml_data["headline"] = parsed_xml.find_all("recordtitle")[0].gettext()
    xml_data["pub_date"] = parsed_xml.find_all("numericpudate")[0].gettext()
    xml_data["start_page"] = parsed_xml.find_all("startpage")[0].gettext()
    xml_data["web_url"] = parsed_xml.find_all("urldocview")[0].gettext()
    xml_data["fulltext"] = parsed_xml.find_all("fulltext")[0].gettext()
    
    return xml_data
    









"""
def write_full_text(xmlpath):
   
    
    with open(xmlpath) as input_file: 
        raw_html = input_file.read()
        parsed_html = bs4.BeautifulSoup(raw_html, "lxml")
        text_tags = parsed_html.find_all("fulltext")
        
        text_tags = text_tags[0].get_text()
        
        with open('a.txt', 'w') as output_file:
            output_file.write(text_tags)
"""

#-------------------------------------------------------------------------------
# Globals and Calls
#-------------------------------------------------------------------------------
if __name__ == "__main__":
    
    #define which zip file to use REPLACE LATER WITH FOR-LOOP
    zip_files_path = r'..\ZIP'
    zip_file_name = r'xml2.zip'
    zip_file_path = os.path.join(zip_files_path, zip_file_name)

for raw_xml in xml_generator(zip_file_path):
    sampledata = get_data(raw_xml)
    print(sampledata)




            
    
    
        



    