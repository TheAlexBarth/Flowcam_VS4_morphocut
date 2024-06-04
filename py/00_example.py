import os, os.path
import tkinter as tk
from tkinter import filedialog
from morphocut.core import Pipeline
from morphocut.file import Find
from morphocut.integration.flowcam import FlowCamReader
from morphocut.image import RGB2Gray, ImageProperties
from morphocut.stream import Filter, TQDM
from morphocut.str import Format
from morphocut.contrib.ecotaxa import EcotaxaWriter
from morphocut.contrib.zooprocess import CalculateZooProcessFeatures

# prompt for choosing folder
root = tk.Tk()
root.attributes('-topmost', 1)
root.withdraw()
raw_folder_path = filedialog.askdirectory()
root.update()
os.chdir(raw_folder_path)

# make directory for extraction
output_path = os.path.join(os.path.dirname(raw_folder_path), "morphocut")
if not os.path.exists(output_path): os.mkdir(output_path)

# print folder names
print("Selected folder: " + raw_folder_path)
print("Files will be extracted to: " + output_path)

# MorphoCut pipeline
if __name__ == "__main__":

    with Pipeline() as p:
        # [Stream] Find .lst files in input path
        lst_fn = Find(raw_folder_path, [".lst"])

        # [Stream] Read objects from a .lst file
        obj = FlowCamReader(lst_fn)
           
        # Extract object image and convert to gray level
        img = obj.image
        img_gray = RGB2Gray(img, True)
        
        # Extract object mask
        mask = obj.mask

        # Extract metadata from the FlowCam
        object_meta = obj.data

        # Construct object ID
        object_id = Format("{lst_name}_{id}", lst_name = obj.lst_name, _kwargs = object_meta)
        object_meta["id"] = object_id

        # Calculate object properties (area, eccentricity, equivalent_diameter, mean_intensity, ...). See skimage.measure.regionprops.
        regionprops = ImageProperties(mask, img_gray)
        
        # ---- Size filter ----
        # [Stream] Only keep large images
        #Filter(regionprops['convex_area']>1499)
        
        # Append object properties to metadata in a ZooProcess-like format
        object_meta = CalculateZooProcessFeatures(regionprops, object_meta)
               
        # [Stream] Here, the images and EcoTaxa table are saved and zipped.
        EcotaxaWriter(
            os.path.join(output_path, "EcoTaxa.zip"),
            [
                # The original RGB image
                (Format("{object_id}.jpg", object_id = object_id), img),
            ],
            object_meta = object_meta,
        )

        # Progress bar
        TQDM(object_id)

p.run()# Requires MorphoCut developer version.