===============================================================
                         EmberSort
===============================================================

EmberSort is a simple and powerful Python module that automatically
organizes files in a folder into categorized subfolders based on 
their file types.

It works on Windows, macOS, and Linux. You can use both backslashes (\)
and forward slashes (/) in paths — no need for raw strings (r"").

---------------------------------------------------------------
INSTALLATION
---------------------------------------------------------------

If uploaded to PyPI:
    pip install EmberSort

If using locally:
    1. Place "ember_sort.py" in your project folder.
    2. Import and use it directly in your Python script.

---------------------------------------------------------------
USAGE
---------------------------------------------------------------

Example usage:

    from ember_sort import organise

    organise("C:\\Path\\To\\Your\\Folder")
    organise("C:/Path/To/Your/Folder")   # Works too!

The function will automatically create categorized folders and
move files accordingly.

---------------------------------------------------------------
FUNCTIONS
---------------------------------------------------------------

1. createFolder(path)
   ------------------
   Creates a folder if it doesn’t already exist.

   Parameters:
       path (str) — The folder path to create.

   Example:
       createFolder("C:/Users/Example/Documents/Images")


2. moveFile(filePath, folderPath)
   ------------------------------
   Moves a file to a target folder. If a file with the same name
   already exists, the new file is automatically renamed.

   Parameters:
       filePath (str) — The file to move.
       folderPath (str) — The folder where it should go.

   Example:
       moveFile("C:/Downloads/file.txt", "C:/Downloads/text_documents")


3. categorize(filePath, baseFile)
   -------------------------------
   Detects the file type and moves it into the correct category
   (e.g., images, videos, audio, etc.). Files that don’t match any
   category are placed in an "others" folder.

   Parameters:
       filePath (str) — Path of the file.
       baseFile (str) — The main folder containing the file.

   Example:
       categorize("C:/Downloads/photo.jpg", "C:/Downloads")


4. organise(baseFile)
   ------------------
   Organizes all files in the given folder into categorized
   subfolders. This is the main function you’ll use.

   Parameters:
       baseFile (str) — The folder path to organize.

   Example:
       organise("C:/Downloads")

---------------------------------------------------------------
SUPPORTED FILE CATEGORIES
---------------------------------------------------------------

Text Documents:  .txt, .doc, .docx, .pdf, .md, .csv, .rtf
Spreadsheets:    .xls, .xlsx, .ods, .csv
Presentations:   .ppt, .pptx, .odp, .key
Images:          .jpg, .png, .gif, .svg, .webp
Audio:           .mp3, .wav, .aac, .flac
Video:           .mp4, .mkv, .avi, .mov
Archives:        .zip, .rar, .7z, .tar
Programming:     .py, .c, .cpp, .js, .java, .html, .css
Executables:     .exe, .msi, .apk
Databases:       .db, .sqlite, .sql
Web Files:       .html, .css, .js, .php
eBooks:          .epub, .mobi, .fb2
3D/Game Files:   .obj, .fbx, .stl, .pak
AI/ML Files:     .pt, .h5, .onnx
Others:          Any unrecognized files.

---------------------------------------------------------------
EXAMPLE DIRECTORY BEFORE & AFTER
---------------------------------------------------------------

Before running organise("C:/Downloads"):

C:/Downloads/
├── photo.jpg
├── song.mp3
├── report.docx
├── video.mp4
├── unknown.xyz

After running organise("C:/Downloads"):

C:/Downloads/
├── images/
│   └── photo.jpg
├── audio/
│   └── song.mp3
├── text_documents/
│   └── report.docx
├── video/
│   └── video.mp4
├── others/
│   └── unknown.xyz

---------------------------------------------------------------
NOTES
---------------------------------------------------------------

- Works on all operating systems.
- Automatically handles duplicate file names.
- Automatically fixes path format — no need for raw strings.
- Perfect for cleaning messy folders.

---------------------------------------------------------------
CREDITS
---------------------------------------------------------------

Created by: Jugashish Chetia  
Project: EmberSort  
License: Free to use and modify with credit.

===============================================================
