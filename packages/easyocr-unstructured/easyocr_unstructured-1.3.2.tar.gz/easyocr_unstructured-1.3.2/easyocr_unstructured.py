#kevin fink
#kevin@shorecode.org
#Wed Dec  4 01:42:15 PM +07 2024
#easyocr_unstructured.py

import numpy as np
import copy
import time
import easyocr
import pdf2image
import hashlib
import json
import os
import gc

class EasyocrUnstructured:
    def __init__(self, init_reader=False, gpu=True):        
        # directory where files are saved to prevent hte slow process of scanning hte pdfs if possible
        self.output_dir = os.path.join('tmp', 'easyocr_unstructured')
        
        if not os.path.exists(self.output_dir):
            new_dir = '.'
            for entry in os.path.split(self.output_dir):                
                new_dir = os.path.join(new_dir, entry)
                if not os.path.exists(new_dir):
                    os.mkdir(new_dir)
        
        # Delete parsed PDF json files older than 7 days in output_dir
        self.delete_old_files(self.output_dir, days=7)        
        
        self.reader = None
        if init_reader:
            self.reader = easyocr.Reader(['en'], gpu=gpu,)

    def delete_old_files(self, directory, days):
        """
        Delete files in the specified directory that are older than a specified number of days.
    
        This method iterates through all files in the given directory and checks their last modified 
        time. If a file's last modified time is older than the specified number of days, the file 
        will be deleted.
    
        Parameters:
        directory (str): The path to the directory where files will be checked and potentially deleted.
        days (int): The age threshold in days. Files older than this threshold will be deleted.
    
        Returns:
        None: This method does not return any value. It performs file deletions as a side effect.
    
        Example:
        >>> self.delete_old_files('/path/to/directory', 7)
        This will delete all files in '/path/to/directory' that are older than 7 days.
        """        
        # Get the current time
        now = time.time()
        # Calculate the threshold time
        threshold = now - (days * 86400)  # 86400 seconds in a day

        # Iterate through the files in the directory
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            # Check if it's a file (not a directory)
            if os.path.isfile(file_path):
                # Get the last modified time
                file_mod_time = os.path.getmtime(file_path)
                # Delete the file if it's older than the threshold
                if file_mod_time < threshold:
                    os.remove(file_path)
                    print(f"Deleted old file: {file_path}")  # Optional: log the deletion

    
    def get_new_entry(self, entry):
        """
        Convert an entry into a new bounding box format.
    
        This function takes an entry consisting of bounding box coordinates, 
        text, and probability, and returns a modified bounding box that includes 
        the text as the last element.
    
        Args:
            entry (tuple): A tuple containing the bounding box, text, and probability.
    
        Returns:
            list: A list containing the modified bounding box with the text appended.
        """
        (bbox, text, prob) = entry
        bbox = [[int(coord) for coord in point] for point in bbox]
        bbox.append(text)
        return bbox
    
    def scan_pdf(self, pdf_path,**kwargs):
        """Scan a PDF file and extract text from its pages using the EasyOCR library.
    
        Args:
            pdf_path (str): The path to the PDF file to be scanned.
    
        Returns:
            list: A list of bounding boxes and corresponding text extracted from the PDF.
                  Each entry in the list is a list containing the bounding box coordinates
                  followed by the extracted text.
        """
        gpu = kwargs.get('gpu', True)
        dpi = kwargs.get('dpi', 120)
        batch_size = kwargs.get('batch_size', 3)
        if self.reader:
            reader = self.reader
        else:            
            reader = easyocr.Reader(['en'], gpu=gpu, )  # Specify the language(s) you want to use        
        results = []
        try:            
            images = pdf2image.convert_from_path(pdf_path, grayscale=True, dpi=dpi)
            if len(images) == 0:
                return []
            images_resized = list()
            for image in images:
                images_resized.append(image.resize(
                    [
                        int(image.size[0] * 0.65),
                        int(image.size[1] * 0.65)
                    ]
                ))
            detections = dict()
            for i in range(0, len(images_resized), batch_size):
                detection_list = reader.readtext_batched(
                    [np.array(img) for img in images_resized][i:i + batch_size],
                    batch_size=batch_size,
                    text_threshold=0.4,
                    min_size=1, 
                    low_text = 0.2,                    
                    bbox_min_size=1,
                    bbox_min_score = 0.15,
                    filter_ths = 0.0008,
                    link_threshold=0.2, 
                )
                for page_num, detection in enumerate(detection_list):
                    detections[page_num+i] = detection
                gc.collect()
            results = {k: list(map(self.get_new_entry, entry)) for k, entry in detections.items()}
            del images
        except Exception as e:
            print(f'ERROR PROCESSING PDF: {e}')
        return results
    
    def add_new_entry(self, current_group, bbox, entry):
        """
        Add a new entry to the current group if the text is different from the last entry.
    
        This function appends the current entry to the current group and 
        updates the processed entries list. It also keeps track of the 
        last bounding box for future proximity checks.
    
        Args:
            current_group (list): The list of currently grouped entries.
            bbox (list): The bounding box coordinates of the current entry.
            entry (tuple): The current entry being processed.

        Returns:
            tuple: A tuple containing:
                - current_group (list): The updated list of currently grouped entries.
                - entries_processed (list): The updated list of processed entries.
                - last_bbox (list): The bounding box of the last entry added to the group.
        """
    
        current_group.append(entry)
        last_bbox = bbox
        return current_group, last_bbox
    
    def are_close(self, bbox1, bbox2, left_max, right_max, threshold):
        """Check if two bounding boxes are within proximity threshold."""
        # x1, y1 = top-left of box
        # x2, y2 = bottom-right of box
        left, top = bbox1[0]
        right, bottom = bbox1[2]
        
        left2, top2 = bbox2[0]
        right2, bottom2 = bbox2[2]
    
        horizontal_valid = right <= left2 - threshold
        vertical_valid = top >= top2 - threshold
        
        new_line = bottom != bottom2
        
        if new_line:
            horizontal_valid = right2 <= right_max and left2 >= left_max
            vertical_valid = bottom <= top2 - threshold
    
        return horizontal_valid and vertical_valid
    
    
    def group_entries(self, entries, threshold):
        """Group entries by proximity."""
        groups = []
        used = set()
    
        for i, entry in enumerate(entries):
            if i in used:
                continue
    
            group = [entry]
            used.add(i)
            bbox_i = entry[:4]
            left_max = bbox_i[0][0]
            right_max = bbox_i[2][0]
    
            for j in range(i + 1, len(entries)):
                if j in used:
                    continue
                bbox_j = entries[j][:4]
    
                if self.are_close(bbox_i, bbox_j, left_max, right_max, threshold):
                    bbox_i = bbox_j
                    if bbox_i[0][0] < left_max:
                        left_max = bbox_i[0][0]
                    if bbox_i[2][0] > right_max:
                        right_max = bbox_i[2][0]
                    
                    group.append(entries[j])
                    used.add(j)
    
            groups.append(group)
    
        return groups
    
    def process_entries(self, entries, proximity_in_pixels):
        """
        Groups text entries based on their bounding box proximity.
        """
        grouped_results = dict()
        for k, v in entries.items():            
            v.sort(key=lambda x: (x[0][1], x[0][0]))  # Sort by top-left Y, then X    
            result = self.group_entries(v, proximity_in_pixels)
            grouped_results[k] = result
    
        return grouped_results
    
    def pdf_to_json(self, pdf_fp, output_fp, **kwargs):
        """
            Convert the contents of a PDF file to a JSON format.
        
            This function scans the PDF file specified by the file path and 
            saves a list of the coordinates and text for each entry in a JSON file.
        
            Args:
                pdf_fp (str): The file path to the PDF file to be scanned.
        
            Returns:
                list: A list of entries extracted from the PDF.
            """    
        entries = self.scan_pdf(pdf_fp, **kwargs)
        with open(output_fp, 'w') as f:
            json.dump(entries, f)
        return entries
    
    def get_hash(self, pdf_fp):
        """
            Generate a SHA-1 hash for the specified PDF file.
        
            This function reads the PDF file in binary mode and computes its 
            SHA-1 hash to create a unique identifier for the file.
        
            Args:
                pdf_fp (str): The file path to the PDF file.
        
            Returns:
                str: The hexadecimal representation of the SHA-1 hash of the file.
            """    
        hash_func = hashlib.sha1()
        with open(pdf_fp, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_func.update(chunk)
        hash_value = hash_func.hexdigest()
        return hash_value
    
    def invoke(self, pdf_fp, proximity_in_pixels=20, gpu=True, dpi=120, batch_size=3, **kwargs):
        """
            Process a PDF file and group text entries by proximity.
        
            This function generates a unique output filename based on the 
            hash of the PDF file. If the output file already exists, it 
            loads the entries from the existing file; otherwise, it scans 
            the PDF and creates a new JSON file. The entries are then 
            grouped by proximity and filtered to keep only the text.
        
            Args:
                pdf_fp (str): The file path to the PDF file to be processed.
                proximity_in_pixels (int, optional): The proximity threshold 
                    for grouping text entries. Defaults to 20.
                gpu (bool): Toggle to compute on GPU, if True and there is
                    no gpu, will use cpu
                dpi (int): DPI setting for parsing PDF, higher value
                    will be more accurate but slower and use more memory
                batch_size (int): Will determine the batch size for both
                    parsing pdfs and scanning them
        
            Returns:
                dict: A dictionary of text entries grouped by proximity.
                    Keyed by page number.
            """    
        #Add hash to filename to ensure it is unique
        hash_value = self.get_hash(pdf_fp)
        #Output to data/output as specified in eut_filepaths.
        #This will reduce processing time drastically if the same file is processed more than once
        output_fp = os.path.join(self.output_dir, hash_value+os.path.split(os.path.splitext(pdf_fp)[0]+'.txt')[-1])
        if not os.path.exists(output_fp):
            #Scan the pdf and create a json file with location of text and actual text
            entries = self.pdf_to_json(pdf_fp, output_fp, gpu=gpu, dpi=dpi, batch_size=batch_size)
        else:
            with open(output_fp, 'r') as f:
                try:                
                    entries = json.load(f)
                except:
                    entries = self.pdf_to_json(pdf_fp, output_fp, gpu=gpu, dpi=dpi, batch_size=batch_size)
        # group entries by proximity
        result =  self.process_entries(entries, proximity_in_pixels)
        #Filter result to only keep text, remove coordinates
        final_result = dict()
        for k, entry in result.items():            
            final_result[k] = [list(map(lambda x: x[4], v)) for v in entry]
        return final_result


if __name__ == '__main__':
    import sys
    sys.exit(0)
