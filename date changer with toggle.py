#Date changer program#

import os
import subprocess
from datetime import datetime
from tkinter import Tk, Label, Button, Entry, StringVar, filedialog, Text, Scrollbar, VERTICAL, END, Checkbutton, IntVar
from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
import piexif
from PIL import Image

def get_file_dates(file_path):
    created = os.path.getctime(file_path)
    modified = os.path.getmtime(file_path)
    return created, modified

def set_file_dates(file_path, created, modified):
    os.utime(file_path, (created, modified))
    created_str = datetime.fromtimestamp(created).strftime('%m/%d/%Y %H:%M:%S')
    modified_str = datetime.fromtimestamp(modified).strftime('%m/%d/%Y %H:%M:%S')
    subprocess.run(['SetFile', '-d', created_str, file_path])
    subprocess.run(['SetFile', '-m', modified_str, file_path])

def get_media_dates(file_path):
    parser = createParser(file_path)
    if not parser:
        return None, None
    metadata = extractMetadata(parser)
    if not metadata:
        return None, None

    try:
        created = metadata.get('creation_date')
    except ValueError:
        created = None

    try:
        modified = metadata.get('modification_date')
    except ValueError:
        modified = None

    return created, modified

def set_media_dates(file_path, created, modified):
    print(f"Setting media created date to: {created}")
    print(f"Setting media modified date to: {modified}")

def copy_exif_data(input_file_path, output_file_path):
    try:
        exif_dict = piexif.load(input_file_path)
        exif_bytes = piexif.dump(exif_dict)
        piexif.insert(exif_bytes, output_file_path)
    except Exception as e:
        print(f"Error copying EXIF data from {input_file_path} to {output_file_path}: {e}")

def copy_quicktime_metadata(input_file_path, output_file_path):
    try:
        exiftool_path = '/usr/local/bin/exiftool' # Adjust this path based on the output of `which exiftool`
        subprocess.run([exiftool_path, '-overwrite_original', '-TagsFromFile', input_file_path, '-CreateDate', '-ModifyDate', output_file_path], check=True)
        print(f"Copied QuickTime metadata from {input_file_path} to {output_file_path}")
    except subprocess.CalledProcessError as e:
        print(f"Error copying QuickTime metadata: {e}")

def browse_input_folder(root):
    folder_path = filedialog.askdirectory()
    input_folder.set(folder_path)
    root.config(bg='SystemButtonFace')  # Reset background color to default
    status_text.delete('1.0', END)  # Clear status text box
    console_text.delete('1.0', END)  # Clear console text box
    root.focus_force()

def browse_output_folder(root):
    folder_path = filedialog.askdirectory()
    output_folder.set(folder_path)
    root.config(bg='SystemButtonFace')  # Reset background color to default
    status_text.delete('1.0', END)  # Clear status text box
    console_text.delete('1.0', END)  # Clear console text box
    root.focus_force()

def update_dates(root):
    in_folder = input_folder.get()
    out_folder = output_folder.get()

    if not os.path.isdir(in_folder):
        status_text.insert(END, "Invalid input folder path.\n")
        return

    if not os.path.isdir(out_folder):
        status_text.insert(END, "Invalid output folder path.\n")
        return

    for subdir, _, files in os.walk(in_folder):
        for filename in files:
            input_file_path = os.path.join(subdir, filename)
            
            if ignore_extension.get() == 1:
                filename_without_ext = os.path.splitext(filename)[0]
                matching_file = None
                for f in os.listdir(out_folder):
                    if os.path.splitext(f)[0] == filename_without_ext:
                        matching_file = f
                        break
                if matching_file:
                    output_file_path = os.path.join(out_folder, matching_file)
                else:
                    status_text.insert(END, f"No matching file found for {filename} in output folder.\n")
                    console_text.insert(END, f"No matching file found for {filename} in output folder.\n")
                    continue
            else:
                relative_path = os.path.relpath(input_file_path, in_folder)
                output_file_path = os.path.join(out_folder, relative_path)

            if os.path.isfile(input_file_path) and os.path.isfile(output_file_path):
                # Get and set file dates
                created, modified = get_file_dates(input_file_path)
                set_file_dates(output_file_path, created, modified)
                status_text.insert(END, f"Updated file dates for {filename}\n")
                console_text.insert(END, f"Processing {filename}\n")
                console_text.insert(END, f" Input created: {datetime.fromtimestamp(created)}\n")
                console_text.insert(END, f" Input modified: {datetime.fromtimestamp(modified)}\n")
                console_text.insert(END, f" Output created set to: {datetime.fromtimestamp(created)}\n")
                console_text.insert(END, f" Output modified set to: {datetime.fromtimestamp(modified)}\n")
                
                # Get and set media dates
                media_created, media_modified = get_media_dates(input_file_path)
                if media_created or media_modified:
                    set_media_dates(output_file_path, media_created, media_modified)
                    status_text.insert(END, f"Updated media dates for {filename}\n")
                    if media_created:
                        console_text.insert(END, f" Input media created: {media_created}\n")
                        console_text.insert(END, f" Output media created set to: {media_created}\n")
                    if media_modified:
                        console_text.insert(END, f" Input media modified: {media_modified}\n")
                        console_text.insert(END, f" Output media modified set to: {media_modified}\n")
                else:
                    status_text.insert(END, f"No media dates available for {filename}\n")
                    console_text.insert(END, f"No media dates available for {filename}\n")

                # Copy EXIF data
                copy_exif_data(input_file_path, output_file_path)
                status_text.insert(END, f"Copied EXIF data for {filename}\n")
                console_text.insert(END, f"Copied EXIF data for {filename}\n")

                # Copy QuickTime metadata
                copy_quicktime_metadata(input_file_path, output_file_path)
                status_text.insert(END, f"Copied QuickTime metadata for {filename}\n")
                console_text.insert(END, f"Copied QuickTime metadata for {filename}\n")
            else:
                status_text.insert(END, f"File {filename} does not exist in output folder.\n")
                console_text.insert(END, f"File {filename} does not exist in output folder.\n")
                
    root.config(bg='green')  # Set background color to green on completion
    root.focus_force()

def main():
    global input_folder, output_folder, status_text, console_text, ignore_extension

    root = Tk()
    root.title("File Date Sync Tool")
    root.geometry("1000x450")  # Increased height for the new toggle button

    input_folder = StringVar()
    output_folder = StringVar()
    ignore_extension = IntVar()  # Variable for the toggle button

    Label(root, text="Input Folder:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
    Entry(root, textvariable=input_folder, width=25).grid(row=0, column=1, padx=10, pady=5)
    Button(root, text="Browse", command=lambda: browse_input_folder(root)).grid(row=0, column=2, padx=10, pady=5)

    Label(root, text="Output Folder:").grid(row=1, column=0, padx=10, pady=5, sticky='e')
    Entry(root, textvariable=output_folder, width=25).grid(row=1, column=1, padx=10, pady=5)
    Button(root, text="Browse", command=lambda: browse_output_folder(root)).grid(row=1, column=2, padx=10, pady=5)

    Button(root, text="Update Dates", command=lambda: update_dates(root)).grid(row=2, column=1, padx=10, pady=10)

    # Add the toggle button to ignore file extensions
    Checkbutton(root, text="Ignore File Extension", variable=ignore_extension).grid(row=2, column=2, padx=10, pady=10)

    status_text = Text(root, wrap='word', height=15, width=45)
    status_text.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky='nw')

    scroll1 = Scrollbar(root, command=status_text.yview, orient=VERTICAL)
    scroll1.grid(row=3, column=2, sticky='nsw')
    status_text.config(yscrollcommand=scroll1.set)

    console_text = Text(root, wrap='word', height=15, width=45)
    console_text.grid(row=3, column=3, columnspan=2, padx=10, pady=5, sticky='ne')

    scroll2 = Scrollbar(root, command=console_text.yview, orient=VERTICAL)
    scroll2.grid(row=3, column=5, sticky='nsw')
    console_text.config(yscrollcommand=scroll2.set)

    root.mainloop()

if __name__ == "__main__":
    main()
