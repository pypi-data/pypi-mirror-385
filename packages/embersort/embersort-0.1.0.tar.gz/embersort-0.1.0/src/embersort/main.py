import os
import shutil
from pathlib import Path

file_formats = {
    "text_documents": [".txt", ".doc", ".docx", ".pdf", ".rtf", ".odt", ".tex", ".md", ".csv", ".tsv", ".log"],
    "spreadsheets": [".xls", ".xlsx", ".ods", ".csv", ".tsv", ".xlsm"],
    "presentations": [".ppt", ".pptx", ".odp", ".key"],
    "images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif", ".webp", ".svg", ".ico", ".heic"],
    "audio": [".mp3", ".wav", ".aac", ".flac", ".ogg", ".wma", ".m4a"],
    "video": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm", ".3gp"],
    "archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2", ".xz", ".iso"],
    "programming": [".c", ".cpp", ".cc", ".h", ".hpp", ".py", ".java", ".js", ".ts", ".html", ".css",
                    ".php", ".rb", ".swift", ".kt", ".go", ".rs", ".sh", ".bat", ".json", ".xml",
                    ".yml", ".yaml", ".sql", ".ini"],
    "executables": [".exe", ".msi", ".apk", ".ipa", ".bin", ".dll", ".sys", ".deb", ".rpm", ".app"],
    "databases": [".db", ".sqlite", ".sqlite3", ".mdb", ".accdb", ".sql"],
    "web_files": [".html", ".htm", ".css", ".js", ".json", ".xml", ".php", ".asp", ".aspx", ".jsp"],
    "ebooks": [".epub", ".mobi", ".azw", ".azw3", ".fb2", ".lit", ".djvu"],
    "game_3d": [".obj", ".fbx", ".stl", ".blend", ".unity", ".pak", ".sav"],
    "ai_ml": [".pt", ".h5", ".onnx", ".pb", ".tflite", ".pkl"]
}


def createFolder(path):
    path = os.path.normpath(path)
    if not os.path.exists(path):
        os.makedirs(path)


def moveFile(filePath, folderPath):
    filePath = os.path.normpath(filePath)
    folderPath = os.path.normpath(folderPath)

    baseFile = os.path.basename(filePath)
    newPath = os.path.join(folderPath, baseFile)

    count = 1
    while os.path.exists(newPath):
        name, ext = os.path.splitext(baseFile)
        newPath = os.path.join(folderPath, f"{name}_{count}{ext}")
        count += 1

    shutil.move(filePath, newPath)


def categorize(filePath, baseFile):
    baseFile = os.path.normpath(baseFile)
    filePath = os.path.normpath(filePath)
    ext = os.path.splitext(filePath)[1].lower()

    for cat, exten in file_formats.items():
        if ext in exten:
            catFolder = os.path.join(baseFile, cat)
            createFolder(catFolder)
            moveFile(filePath, catFolder)
            return


    otherFolder = os.path.join(baseFile, "others")
    createFolder(otherFolder)
    moveFile(filePath, otherFolder)


def organise(baseFile):
    baseFile = os.path.normpath(baseFile)

    for item in os.listdir(baseFile):
        itemPath = os.path.join(baseFile, item)
        if os.path.isfile(itemPath):
            categorize(itemPath, baseFile)



