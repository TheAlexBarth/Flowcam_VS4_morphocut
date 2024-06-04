# A Messy FlowCam Data Sorting
Many older flowcam data sets are stored as a strange mixture of collage files. Fortunately, Simon-Martin Schroder's fantastic [MorphoCut](https://morphocut.readthedocs.io/en/stable/authors.html) library can process these collages quickly. A great example of this application for FlowCam is available in the documentation. However, I had a very large dataset of old FlowCam data which needed to be cleaned, and some important metadata needed to be transferred over.

Under the default MorphoCut-FlowCam pipeline, critical metadata are left behind. I figured I'd make my scripts open for this project for anyone who may encounter similar issues.

While this can't be publically ran since I can't share all data easily, the scripts may be nice. If you have questions don't hesitate to reach out!

# ./py
Scripts related to processing data, morphocut/zooprocess formatting, etc

### Morphocut:
 - 00_example.py: original script from Sari Giering (https://sarigiering.co/posts/from-flowcam-to-ecotaxa/)

### Metadata management:
The first couple metadata scripts are just to deal with the messiness of the directory names and move files around
this is all local work on the data, which are in folders. the index corresponds to a subdirectory full of more subdirectories of visual spreadsheet runs.
 - 01_metafix_badnames.py: a script to fix a typo in the badnames folder.
 - run_file_reader.py: a script to read run file into a dataframe
 - metamgmt.py: utilites for reading and processing metadata files