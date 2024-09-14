This project was written to solve an issue with Google Photos and dates with video files. My digital camera produces large video files, and after compressing them with tools like HandBrake or other video compressors, the new files no longer retained the original metadata. As a result, the videos didn't appear in the correct order when viewed in Google Photos. This should work with other services too such as Amazon photos.

In order to run this project, you need to make sure the following libraries are installed:

- hachoir (Install via pip install hachoir)
- piexif (Install via pip install piexif)
- PIL (Python Imaging Library) – This is part of the Pillow package (Install via pip install Pillow)

Select the input folder, and output folder. 
The file names need to be exactly the same - case doesn't matter
You can choose to ignore file extnesions if you are moving from .mov to mp4 as an example
Once done, the window should turn green. 

If you want to make any changes, feel free, just let me know as i'd love to see it improve. 
