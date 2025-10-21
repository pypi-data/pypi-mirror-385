#!/usr/bin/env python3
"""
meta_reader.py

Extracts metadata from microscopy data directories.
Supports both 3i (Intelligent Imaging Innovations) and Mini2P microscopes.
"""

import yaml
import os
import sys
import xml.etree.ElementTree as ET
import re
import csv
import argparse
from pathlib import Path
import pickle
import json
import pandas as pd

# -------------- CLASS --------------
class DataFrameDict(dict):
    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(key)
    
    def __setattr__(self, key, value):
        self[key] = value

# ------------- FUNCTIONS -------------
def open_overwrite(path, *args, **kwargs):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.unlink(missing_ok=True)
    return open(path, *args, **kwargs) 

def load_classes(yaml_path):
    classes = {}
    with open(yaml_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split on "StartClass:", then re-add it to each chunk
    chunks = ["StartClass:" + c for c in content.split("StartClass:") if c.strip()]

    for chunk in chunks:
        try:
            data = yaml.safe_load(chunk)

            if not isinstance(data, dict):
                continue

            class_data = data.get("StartClass", {})
            class_name = class_data.get("ClassName")
            if not class_name:
                continue

            # ✅ If class_name already exists, turn it into a list
            if class_name in classes:
                if isinstance(classes[class_name], list):
                    classes[class_name].append(class_data)
                else:
                    classes[class_name] = [classes[class_name], class_data]
            else:
                classes[class_name] = class_data

        except yaml.YAMLError as e:
            print("YAML parse error in chunk:\n", chunk[:200], "...", e)

    return classes

def get_organized_experiment_data(yaml_path):
    with open(yaml_path, "r", encoding="utf-8") as f:
        content = f.read()

    chunks = content.strip().split("theTimepointIndex:")

    # --- 1. Parse the Main Data Header ---
    # The header is the very first part, before any time points.
    header_chunk = chunks[0]
    header_metadata = yaml.safe_load(header_chunk.split("EndClass:")[0] + "EndClass: CDataTableHeaderRecord70")
    header = header_metadata.get("StartClass", {})

    # --- 2. Parse the Initial ROI Definitions (from Timepoint 0) ---
    # These are the ROIs defined before any stimulations.
    initial_rois = {}
    if len(chunks) > 1:
        timepoint_zero_chunk = "theTimepointIndex:" + chunks[1]
        sub_chunks = timepoint_zero_chunk.split("StartClass:")
        
        annotations = []
        for ann_chunk in sub_chunks[1:]:
            ann_data = yaml.safe_load("StartClass:" + ann_chunk)
            if ann_data and "StartClass" in ann_data:
                annotations.append(ann_data["StartClass"])
        
        # Organize the initial ROIs into a clean dictionary by their index
        for i, ann in enumerate(annotations):
            if ann.get("ClassName") == 'CCubeAnnotation70':
                roi_id = ann['mRegionIndex']
                if i + 1 < len(annotations):
                    initial_rois[roi_id] = annotations[i + 1]

    # --- 3. Parse and Filter for Stimulation Events (Timepoint 1 onwards) ---
    stimulation_events = []
    # The loop now correctly starts from the third chunk (index 2), skipping the header and timepoint 0.
    for chunk in chunks[2:]:
        full_chunk = "theTimepointIndex:" + chunk
        try:
            sub_chunks = full_chunk.split("StartClass:")
            metadata_part = sub_chunks[0]
            timepoint_metadata = yaml.safe_load(metadata_part)

            annotations = []
            for ann_chunk in sub_chunks[1:]:
                ann_data = yaml.safe_load("StartClass:" + ann_chunk)
                if ann_data and "StartClass" in ann_data:
                    annotations.append(ann_data["StartClass"])
            timepoint_metadata["annotations"] = annotations

            # Now, check if this timepoint is a stimulation event
            frap_annotation = next((ann for ann in annotations if ann.get("ClassName") == "CFRAPRegionAnnotation70"), None)
            
            if frap_annotation:
                stimulation_events.append({
                    "timepoint_index": timepoint_metadata["theTimepointIndex"],
                    "stimulation_data": frap_annotation,
                    "roi_annotations": [ann for ann in annotations if ann.get("ClassName") != "CFRAPRegionAnnotation70"]
                })
        except yaml.YAMLError as e:
            print(f"Skipping problematic chunk due to YAML error: {e}")
            continue

    return {
        "header": header,
        "initial_rois": initial_rois,
        "stimulation_events": stimulation_events
    }

def parse_stimulation_xml(xml_string):
    """
    Cleans and parses the escaped XML string from the annotation file.

    Args:
        xml_string (str): The XML data string with escaped characters.

    Returns:
        dict: A dictionary containing the extracted metadata, or None if parsing fails.
    """
    # --- 1. Clean the XML String ---
    # This replacement map handles the specific escaped characters.
    replacements = {
        '_#60;': '<',
        '_#62;': '>',
        '_#34;': '"',
        '_#32;': ' ',
        '_#10;': '\n',
        '_#58;': ':',
        '_#91;': '[',
        '_#93;': ']'
    }
    
    for old, new in replacements.items():
        xml_string = xml_string.replace(old, new)

    # --- 2. Parse the Cleaned XML and Extract Data ---
    try:
        root = ET.fromstring(xml_string)
        
        # Find the <Description> tag, which contains the most useful info
        description_tag = root.find('.//Description')
        if description_tag is None:
            return None

        # Extract the full description attribute
        description_text = description_tag.get('Description', '')

        # --- 3. Extract Key Values from the Description Text ---
        # Use regular expressions to find the timepoint and ROI list
        timepoint_match = re.search(r'timepoint: (\d+)', description_text)
        roi_match = re.search(r'ROI: ([\d\s]+)power', description_text)

        timepoint = int(timepoint_match.group(1)) if timepoint_match else None
        
        rois = []
        if roi_match:
            # Split the string of numbers and convert each to an integer
            rois = [int(n) for n in roi_match.group(1).strip().split()]

        return {
            'device_name': root.find('.//Device').get('LongName'),
            'duration_ms': int(root.find('.//Duration').get('Time')),
            'description_text': description_text,
            'event_timepoint_ms': timepoint,
            'stimulated_rois': rois
        }

    except ET.ParseError as e:
        print(f"Error parsing XML: {e}")
        return None

def extract_roi_info(events):
    all_events_roi_data = []
    
    for event in events:
        event_info = {
        "timepoint_index": event['timepoint_index'],
        "rois": []
        }

        roi_annotations = event['roi_annotations']
        organized_rois = {}

        for i, ann in enumerate(roi_annotations):
            if ann.get('ClassName') == 'CCubeAnnotation70':
                roi_id = ann.get('mRegionIndex')
                if i + 1 < len(roi_annotations):
                    organized_rois[roi_id] = roi_annotations[i + 1]

        for roi_id, roi_data in organized_rois.items():
            # Get the pixel coordinates from StructArrayValues
            coords = roi_data.get('StructArrayValues', [])
            
            # Format the coordinates into two (X, Y) points
            point1 = (coords[0], coords[1], coords[2]) if len(coords) >= 3 else None
            point2 = (coords[3], coords[4], coords[5]) if len(coords) >= 6 else None

            event_info["rois"].append({
                "roi_index": roi_id,
                "target_power": roi_data.get('mTargetPower'),
                "corner_1_xyz": point1,
                "corner_2_xyz": point2
            })
        
        all_events_roi_data.append(event_info)
    return all_events_roi_data


def process_i3_folder(folder_path: str):
    """
    Process 3i microscope data from a folder containing .yaml files.
    
    Args:
        folder_path: Path to the folder containing .yaml files
    """
    # Read all the files in the folder using yaml
    data = {}
    for filename in os.listdir(folder_path):
        if filename.endswith(".yaml"):
            if filename in ["ImageRecord.yaml", "ChannelRecord.yaml"]:
                with open(os.path.join(folder_path, filename), 'r') as file:
                    try:
                        classes = load_classes(os.path.join(folder_path, filename))
                        data[filename] = classes
                    except yaml.YAMLError as e:
                        print(f"Error reading {filename}: {e}")
            elif filename == "AnnotationRecord.yaml":
                try:
                    content = get_organized_experiment_data(os.path.join(folder_path, filename))
                    data[filename] = content
                except yaml.YAMLError as e:
                    print(f"Error reading {filename}: {e}")
            else:
                with open(os.path.join(folder_path, filename), 'r') as file:
                    try:
                        content = yaml.safe_load(file)
                        data[filename] = content
                    except yaml.YAMLError as e:
                        print(f"Error reading {filename}: {e}")

    base_path = data.get("ImageRecord.yaml", {}).get("CImageRecord70", {})
    fields = ["mDay", "mMonth", "mYear", "mHour", "mMinute", "mSecond"]
    day, month, year, hour, minute, second = (base_path.get(field, "NA") for field in fields)

    # Helper function to safely extract values
    def safe_extract(func, default="NA"):
        """Safely execute a function and return default if it fails."""
        try:
            result = func()
            return result if result is not None else default
        except (KeyError, TypeError, IndexError, AttributeError, ValueError):
            return default

    variables = {
    "device_name": safe_extract(lambda: parse_stimulation_xml(data["AnnotationRecord.yaml"]["stimulation_events"][0]["stimulation_data"]["mXML"])["device_name"] if data["AnnotationRecord.yaml"]["stimulation_events"] else "NA"),
    "n_frames": safe_extract(lambda: data["ElapsedTimes.yaml"]["theElapsedTimes"][0]),
    "pixel_size": safe_extract(lambda: data["ImageRecord.yaml"]["CLensDef70"]["mMicronPerPixel"]),
    "height": safe_extract(lambda: data["ImageRecord.yaml"]["CImageRecord70"]["mHeight"]),
    "width": safe_extract(lambda: data["ImageRecord.yaml"]["CImageRecord70"]["mWidth"]),
    "FOV_size": safe_extract(lambda: f"{data['ImageRecord.yaml']['CLensDef70']['mMicronPerPixel'] * data['ImageRecord.yaml']['CImageRecord70']['mHeight']} x {data['ImageRecord.yaml']['CLensDef70']['mMicronPerPixel'] * data['ImageRecord.yaml']['CImageRecord70']['mWidth']} microns"),
    "Elapsed_time_offset": safe_extract(lambda: data["ImageRecord.yaml"]["CImageRecord70"]["mElapsedTimeOffset"]),
    "green_channel": safe_extract(lambda: data["ImageRecord.yaml"]["CMainViewRecord70"]["mGreenChannel"]),
    "red_channel": safe_extract(lambda: data["ImageRecord.yaml"]["CMainViewRecord70"]["mRedChannel"]),
    "blue_channel": safe_extract(lambda: data["ImageRecord.yaml"]["CMainViewRecord70"]["mBlueChannel"]),
    "X_start_position": safe_extract(lambda: data["ChannelRecord.yaml"]["CExposureRecord70"][0]["mXStartPosition"]),
    "Y_start_position": safe_extract(lambda: data["ChannelRecord.yaml"]["CExposureRecord70"][0]["mYStartPosition"]),
    "Z_start_position": safe_extract(lambda: data["ChannelRecord.yaml"]["CExposureRecord70"][0]["mZStartPosition"]),
    "day": day,
    "month": month,
    "year": year,
    "hour": hour,
    "minute": minute,
    "second": second,
    "stimulation_events": safe_extract(lambda: len([x["timepoint_index"] for x in data["AnnotationRecord.yaml"]["stimulation_events"]]), 0),
    "repetitions": safe_extract(lambda: [
        int(re.search(r"(\d+)\s+repetition", parse_stimulation_xml(event["stimulation_data"]["mXML"])["description_text"]).group(1))
        if parse_stimulation_xml(event["stimulation_data"]["mXML"]) and 
           re.search(r"(\d+)\s+repetition", parse_stimulation_xml(event["stimulation_data"]["mXML"])["description_text"]) 
        else "NA"
        for event in data["AnnotationRecord.yaml"]["stimulation_events"]
    ], []),
    "duty_cycle": safe_extract(lambda: [
        re.search(r"user defined analog:\s+(.*?)\s+1 repetition", parse_stimulation_xml(event["stimulation_data"]["mXML"])["description_text"]).group(1)
        if parse_stimulation_xml(event["stimulation_data"]["mXML"]) and 
           re.search(r"user defined analog:\s+(.*?)\s+1 repetition", parse_stimulation_xml(event["stimulation_data"]["mXML"])["description_text"])
        else "NA"
        for event in data["AnnotationRecord.yaml"]["stimulation_events"]
    ], []),
    "stimulation_timeframes": safe_extract(lambda: [x["timepoint_index"] for x in data["AnnotationRecord.yaml"]["stimulation_events"]], []),
    "stimulation_ms": safe_extract(lambda: [parse_stimulation_xml(x["stimulation_data"]["mXML"])["event_timepoint_ms"] for x in data["AnnotationRecord.yaml"]["stimulation_events"]], []),
    "duration_ms": safe_extract(lambda: [parse_stimulation_xml(x["stimulation_data"]["mXML"])["duration_ms"] for x in data["AnnotationRecord.yaml"]["stimulation_events"]], []),
    "stimulated_rois": safe_extract(lambda: [parse_stimulation_xml(x["stimulation_data"]["mXML"])["stimulated_rois"] for x in data["AnnotationRecord.yaml"]["stimulation_events"]], []),
    "stimulated_roi_powers": safe_extract(lambda: [
        [(x["roi_index"], x["target_power"]) for x in ev["rois"]] for ev in extract_roi_info(data["AnnotationRecord.yaml"]["stimulation_events"])
    ], []),
    "stimulated_roi_location": safe_extract(lambda: [
        [(x["roi_index"], x["corner_1_xyz"], x["corner_2_xyz"]) for x in ev["rois"]] for ev in extract_roi_info(data["AnnotationRecord.yaml"]["stimulation_events"])
    ], []),
    "time_stamps": safe_extract(lambda: data["ElapsedTimes.yaml"]["theElapsedTimes"][1:], []),
    "initial_roi_powers": safe_extract(lambda: [
        (roi_id, roi_data.get('mTargetPower')) for roi_id, roi_data in data["AnnotationRecord.yaml"]["initial_rois"].items()
    ], []),
    "initial_roi_location": safe_extract(lambda: [
        (roi_id, 
         tuple(roi_data.get('StructArrayValues', [])[0:3]), 
         tuple(roi_data.get('StructArrayValues', [])[3:6])) 
        for roi_id, roi_data in data["AnnotationRecord.yaml"]["initial_rois"].items()
    ], [])
    }

    # Validate that list lengths match stimulation_events count
    if variables['stimulation_events'] > 0:
        list_vars = ['stimulation_timeframes', 'stimulation_ms', 'duration_ms', 
                     'repetitions', 'duty_cycle', 'stimulated_rois', 
                     'stimulated_roi_powers', 'stimulated_roi_location']
        
        for var_name in list_vars:
            var_value = variables[var_name]
            if isinstance(var_value, list) and len(var_value) != variables['stimulation_events']:
                print(f"⚠️ Warning: {var_name} has {len(var_value)} entries but {variables['stimulation_events']} events expected.")

    with open(Path(folder_path) / 'experiment_summary.pkl', 'wb') as f:
        # 'wb' is used for writing in binary mode
        pickle.dump(variables, f)

    # Output a json file 
    with open_overwrite(Path(folder_path) / 'experiment_summary.json', 'w', encoding='utf-8') as f:
        json.dump(variables, f, indent=4)

    print(f"JSON file and Pickle file saved to {folder_path}")

    if variables["Elapsed_time_offset"] != "NA" and variables["Elapsed_time_offset"] != 0:   
        print(f"⚠️ Warning: Elapsed time offset is {variables['Elapsed_time_offset']} ms, not zero as expected.")
    if variables["n_frames"] != "NA" and variables["time_stamps"] != "NA" and variables["n_frames"] != len(variables["time_stamps"]):
        print(f"⚠️ Warning: Number of frames ({variables['n_frames']}) does not match length of time stamps ({len(variables['time_stamps'])}).")

    print("\n[OK] Files saved successfully.")


def process_mini2p_folder(folder_path: str):
    """
    Process Mini2P microscope data from a folder containing .tdms files.
    
    Args:
        folder_path: Path to the folder containing subfolders with .tdms files
    """
    try:
        import nptdms
        import pandas as pd
    except ImportError as e:
        print(f"[ERROR] Required package is missing: {e}")
        print("Install with: pip install nptdms pandas")
        sys.exit(1)
    
    print(f"[INFO] Processing Mini2P data from: {folder_path}")
    
    # Helper function to safely extract values
    def safe_extract(func, default="NA"):
        """Safely execute a function and return default if it fails."""
        try:
            result = func()
            return result if result is not None else default
        except (KeyError, TypeError, IndexError, AttributeError, ValueError):
            return default
    
    # Collect all subdirectories and TDMS files
    folders = {}
    path_df = {}
    for subdir in os.listdir(folder_path):
        subdir_path = os.path.join(folder_path, subdir)
        if os.path.isdir(subdir_path):
            folders[subdir] = subdir_path
            tdms_files = [os.path.join(subdir_path, f) for f in os.listdir(subdir_path) if f.endswith('.tdms')]
            if tdms_files:
                path_df[subdir] = tdms_files
    
    # Load TDMS data into nested dict structure
    tdms_data = {}
    for folder_name, tdms_files in path_df.items():
        if folder_name == "SyncInformation":
            continue
        
        if not tdms_files:
            continue
            
        tdms_file_path = tdms_files[0]
        try:
            tdms_file = nptdms.TdmsFile.read(tdms_file_path)
            print(f"[INFO] Loaded {folder_name}")
            
            tdms_data[folder_name] = {}
            for group in tdms_file.groups():
                group_data = {}
                for channel in group.channels():
                    group_data[channel.name] = channel[:]
                
                # Convert to pandas DataFrame for easier manipulation
                if group_data:
                    tdms_data[folder_name][group.name] = pd.DataFrame(group_data)
                    
        except Exception as e:
            print(f"[WARN] Error reading {tdms_file_path}: {e}")
    
    # Extract metadata from the first CellVideo (if available)
    image_info = {}
    if 'CellVideo1' in tdms_data and 'Image_Info' in tdms_data['CellVideo1']:
        info_df = tdms_data['CellVideo1']['Image_Info']
        for _, row in info_df.iterrows():
            image_info[row['Item']] = row['Value']
    elif 'CellVideo2' in tdms_data and 'Image_Info' in tdms_data['CellVideo2']:
        info_df = tdms_data['CellVideo2']['Image_Info']
        for _, row in info_df.iterrows():
            image_info[row['Item']] = row['Value']
    
    # Parse timestamp from image info
    import datetime
    timestamp_str = safe_extract(lambda: image_info.get('Image time', 'NA'))
    if timestamp_str != 'NA':
        try:
            # Parse format like "10/16/2025 11:19:54 PM"
            dt = datetime.datetime.strptime(timestamp_str, "%m/%d/%Y %I:%M:%S %p")
            day = dt.day
            month = dt.month
            year = dt.year
            hour = dt.hour
            minute = dt.minute
            second = dt.second
        except:
            day = month = year = hour = minute = second = "NA"
    else:
        day = month = year = hour = minute = second = "NA"
    
    # Count frames from timing data and detect channels
    n_frames_cell = 0
    n_frames_mice = 0
    time_stamps = []
    has_cha = False
    has_chb = False
    
    for video_name in ['CellVideo1', 'CellVideo2']:
        if video_name in tdms_data:
            for channel in ['CHA', 'CHB']:
                if channel in tdms_data[video_name]:
                    if channel == 'CHA':
                        has_cha = True
                    if channel == 'CHB':
                        has_chb = True
                    n_frames_cell = max(n_frames_cell, len(tdms_data[video_name][channel]))
                    # Extract timestamps if available
                    if 'Time' in tdms_data[video_name][channel].columns:
                        time_col = tdms_data[video_name][channel]['Time']
                        if len(time_col) > len(time_stamps):
                            time_stamps = time_col.tolist()
    
    for video_name in ['MiceVideo1', 'MiceVideo2']:
        if video_name in tdms_data:
            for channel in ['CHA', 'CHB']:
                if channel in tdms_data[video_name]:
                    if channel == 'CHA':
                        has_cha = True
                    if channel == 'CHB':
                        has_chb = True
                    n_frames_mice = max(n_frames_mice, len(tdms_data[video_name][channel]))
    
    # Determine channel configuration
    green_channel = "NA"
    red_channel = "NA"
    blue_channel = "NA"
    
    if has_cha and has_chb:
        green_channel = 1
        red_channel = 2
    elif has_cha:
        green_channel = 1
    
    # Build variables dictionary
    variables = {
        "device_name": "Mini2P",
        "n_frames": safe_extract(lambda: n_frames_cell if n_frames_cell > 0 else n_frames_mice, 0),
        "n_frames_cell": n_frames_cell,
        "n_frames_mice": n_frames_mice,
        "pixel_size": safe_extract(lambda: image_info.get('Image size_Pixel', 'NA')),
        "height": safe_extract(lambda: int(image_info.get('Image size_Line', 'NA'))),
        "width": safe_extract(lambda: int(image_info.get('Image size_Pixel', 'NA'))),
        "FOV_size": "NA",  # Mini2P doesn't provide micron measurements in TDMS
        "zoom": safe_extract(lambda: image_info.get('Zoom', 'NA')),
        "laser_voltage": safe_extract(lambda: image_info.get('Laser(V)', 'NA')),
        "pmt_voltage": safe_extract(lambda: image_info.get('PMT(V)', 'NA')),
        "scan_speed_hz": safe_extract(lambda: image_info.get('Scan speed(Hz)', 'NA')),
        "image_channel": safe_extract(lambda: image_info.get('Image channel', 'NA')),
        "Elapsed_time_offset": 0,  
        "green_channel": green_channel,  
        "red_channel": red_channel,
        "blue_channel": blue_channel,
        "X_start_position": "NA",
        "Y_start_position": "NA",
        "Z_start_position": "NA",
        "day": day,
        "month": month,
        "year": year,
        "hour": hour,
        "minute": minute,
        "second": second,
        "stimulation_events": 0,  # Mini2P stimulation data would need separate processing
        "repetitions": [],
        "duty_cycle": [],
        "stimulation_timeframes": [],
        "stimulation_ms": [],
        "duration_ms": [],
        "stimulated_rois": [],
        "stimulated_roi_powers": [],
        "stimulated_roi_location": [],
        "time_stamps": time_stamps,
        "initial_roi_powers": [],
        "initial_roi_location": [],
        "data_folders": list(tdms_data.keys())
    }
    
    # Save metadata
    with open(Path(folder_path) / 'experiment_summary.pkl', 'wb') as f:
        pickle.dump(variables, f)
    
    with open_overwrite(Path(folder_path) / 'experiment_summary.json', 'w', encoding='utf-8') as f:
        json.dump(variables, f, indent=4)
    
    print(f"[OK] Mini2P metadata saved to {folder_path}")
    print("\n[OK] Files saved successfully.")


def main():
    """Main entry point for the metadata extraction script."""
    parser = argparse.ArgumentParser(
        description='Extract metadata from microscopy data directories.'
    )
    parser.add_argument(
        'directory',
        help='Path to the folder containing microscopy data'
    )
    parser.add_argument(
        '-s', '--source',
        choices=["i3", "mini"],
        required=True,
        help="Microscope source type: 'i3' for 3i microscopes, 'mini' for Mini2P"
    )
    args = parser.parse_args()

    folder_path = os.path.abspath(args.directory)
    
    if not os.path.isdir(folder_path):
        print(f"[ERROR] Directory not found: {folder_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        if args.source == "i3":
            process_i3_folder(folder_path)
        elif args.source == "mini":
            process_mini2p_folder(folder_path)
        else:
            print(f"[ERROR] Unknown source type: {args.source}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"[FATAL] {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
