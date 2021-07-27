import shutil
import os
from tempfile import SpooledTemporaryFile

# file path will be filename + file_id, removes conflict when 
# multiple files is stored with same name
def file_save(file: SpooledTemporaryFile, path):
    with open(path, "wb") as f:
        
        # file was written recently, pointer is at the end of the file
        file.seek(0)
        shutil.copyfileobj(file._file, f)

    # destroy temp file
    file.close()
        
        
def file_delete(path):
    if os.path.exists(path):
        os.remove(path)

def file_exists(path):
    if os.path.exists(path):
        return True
    else:
        return False