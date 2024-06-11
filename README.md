# A Messy FlowCam Data Sorting
Many older flowcam data sets are stored as a strange mixture of collage files. Fortunately, Simon-Martin Schroder's fantastic [MorphoCut](https://morphocut.readthedocs.io/en/stable/authors.html) library can process these collages quickly. A great example of this application for FlowCam is available in the documentation. However, I had a very large dataset of old FlowCam data which needed to be cleaned, and some important metadata needed to be transferred over.

Under the default MorphoCut-FlowCam pipeline, critical metadata are left behind. I figured I'd make my scripts open for this project for anyone who may encounter similar issues.

While this can't be publically ran since I can't share all data, the scripts may be nice for refering to if people have large datasets of flowcam runs on VS4 or earlier. If you have questions don't hesitate to reach out!

### Basic workflow:

All these scripts are in python to keep simplicity with the implementation of morphocut.
- 01_filemove.py: first, all collage files from individual runs must be put into a raw folder with all interested runs together. It is possible to run the morphocut on a single run (as is in the example script form Sari Giering), but often times users likely have many, many runs so it is best to combine.
    - to run, the directory needs to be set on line 4 to the large directory in which all subdirectories of runs are stored.
    - for simplicity down the line, runs should be grouped by similar file naming conventions.
- 02_morphocut_run.py: this script is verbatim from Sari Giering (https://sarigiering.co/posts/from-flowcam-to-ecotaxa/). Running it will pop-up a dialog window and you can select the raw folder created by step one
- 03_run_file_reader.py: this is the crux of this whole project. If you just do step 2, you can upload to ecotaxa but it will leave out critical metadata. You can extract the Ecotaxa zip file in the morphocut directory and use step three to add metadata. There are two main steps. 
    1 - it reads the metadata for each run with the associated run file. Particularly particular parameteres of interest are located on line26. Becareful when editing that it matches the run file and does not conflict (e.g. "run time" and "time" would conflict).
    2 - it reads a custom format of the run name. In my case, there was critical metadata stored in the run name title (e.g. Sitecode_DDMMYY_Rep). So I created custom methods to extract necessary infomration. These are stored in the utilities and called on line 65. These must be edited and changed for individual use case. I relied on a bunch of messy regex to get it done but that can vary from space to space.
    - once the run file reader is complete, it will check that all run files have matching instances in the ecotaxa (etx) tsv file. If there are an issue, it will either warn you or prompt to delete. Once complete, it creates a new ecotaxa tsv file and you can zip it and upload to ecotaxa!


### Warnings and caveats
First, make sure to make a backup of everything prior to actually running it. While most the scripts create new products, the filemove script does take important items out of folders and moves them to raw. This step breaks compatibility with VisualSpreadsheet so it should not be done on the original copy of the data. Also because the main morphocut script is old, I did not bother creating a clean virtual environment. As of creation (2024-June) there are several depreciation warnings. Watch out!
