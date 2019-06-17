# -*- coding: utf-8 -*-
"""
Created on Sat Jun 15 12:43:22 2019

@author: David
"""

r'''
Specifications:
    1 - For a given DyNetML file,
    2 - Find this line:
        <nodeclass type= "resource" id = "Document">
        <node id="C:\Users\David\Documents\Research\toi_08_incomplete\politics08_sample\data\1922533204bjp_gears_up_for_2009_state_polls.txt">
    3 - Use TOI_metadata.csv to look up the publication date
    4 - Modify the MetaNetwork id tag so that it looks like this:
        <MetaNetwork id="Raiders, part 01-Peru" date="1936-11-01T12:00:00+05:30">
'''



import bs4
import pandas
import os



def get_bs4(file_path):

    with open(file_path) as input_file:
        dynetml_raw = input_file.read()
        dynetml_parsed = bs4.BeautifulSoup(dynetml_raw, "xml")

        return dynetml_parsed
    

def add_date(file_path, date, output_file):

    parsed = get_bs4(file_path)

    parsed.MetaNetwork["date"] = date
    output = str(parsed)

    with open(output_file, 'w') as text_file:
        text_file.write(output)

def get_date(file, metadata_df, counter):

    file_name = os.path.split(file)[1]
    file_name = os.path.splitext(file_name)[0]
    file_name = os.path.splitext(file_name)[0]

    date = metadata_df.loc[metadata_df['txt_file'] == file_name].astype(str)
    #date = date.pub_date.astype(str)
    #date = date.loc[0]
    print(date)


    yyyy = date[0:4]
    MM = date[4:6]
    dd = date[6:]
    
    counter +=1
    rmm = counter // 60     #defines rmins as the number of whole minutes in the raw input
    ss = counter % 60        #defines sec as the remaining number of seconds
    rhh = rmm // 60  #defines rhrs as the number of whole hours in the raw input
    mm = rmm % 60   #defines mins as the remaining number of minutes
    hh = rhh % 24     #defines hrs as the remaining number of hours
    ss = str(ss).zfill(2)
    mm = str(mm).zfill(2)
    hh = str(hh).zfill(2)

    date ='{}-{}-{}T{}:{}:{}-05'.format(yyyy,MM,dd,hh,mm,ss)

    return date

def add_date_to_file(file, metadata_df, counter):
    date = get_date(file, metadata_df, counter)
    add_date(file, date, file)    
    
    
if __name__ == "__main__":
    directory = r'C:\Users\David\Documents\Research\toi_08_incomplete\politics08_sample\netmapper_output'
    file = '1922533204bjp_gears_up_for_2009_state_polls.txt.meta.xml'
    metadata_df = pandas.read_csv(r"C:\Users\David\Documents\Research\toi_08_incomplete\politics08_sample\metadata\TOI_metadata.csv")
    counter = 0
    
    for file in os.listdir(directory):
   #     try:
        file = os.path.join(directory, file)
        add_date_to_file(file, metadata_df, counter)
   #     except:
   #         print("exception:",file)
   #         pass    
