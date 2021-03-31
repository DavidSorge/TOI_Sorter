# TOI_Sorter

The Times of India sorter is a script to expeditiously sort .xml files from the Times of India newspaper archive 
into a hierarchical file system by year, month, day, and category.

The script is written with the assumption that it will be run from within a sibling folder to the XML folder.

TOI_Sorter works, but has been deprecated in favor of its cousin, txt_separator

txt_separator uses the zipped Times of India archive, writes the full-text of each article into a directory labelled for the year it was published, and creates a csv file with the metadata from the file.

However, since I was relatively new to python/pandas at the time, both scripts tend to get slower the longer you use them, and thus have significant room for optimization.
