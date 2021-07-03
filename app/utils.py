import shutil
import os

# file path will be filename + file_id, removes conflict when 
# multiple files is stored with same name
def file_save(file, path):
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
        
def file_delete(path):
    if os.path.exists(path):
        os.remove(path)

def file_exists(path):
    if os.path.exists(path):
        return True
    else:
        return False