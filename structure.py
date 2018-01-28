"""
@Project Name - filetypes
@author - Johnathan
@date - 5/11/2017
@time - 2:54 PM

"""
import hashlib
import os
import time
#from errors import *

class File(object):
    def __init__(self, path):
        self.path = self._verify(path)
        self.stat = os.stat(self.path)
        self.size = os.path.getsize(self.path)
        self.file_extension = os.path.splitext(self.path)[1][1:]
        self.name = os.path.basename(self.path)
        self.creation_date = time.strftime("%Y:%m:%d %H:%M:%S", time.localtime(self.stat.st_ctime))
        self.last_modified = time.strftime("%Y:%m:%d %H:%M:%S", time.localtime(self.stat.st_mtime))
        self.type = self.__class__.__name__

    def __repr__(self):
        return self.name

    def hash(self):
        hash_md5 = hashlib.md5()
        with open(self.path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    def _verify(self, path):
        if os.path.isabs(path):
            if os.path.isfile(path):
                file_ext = path.split('.')[-1]
                if hasattr(self, 'acceptable_file_types'):
                    if self.acceptable_file_types:
                        if file_ext.lower() in self.acceptable_file_types:
                            return path
                        else:
                            raise FileTypeError
                            #raise Exception('{} is not an acceptable file extension'.format(file_ext))
                    else:
                        return path
            else:
                raise Exception('{} is not a file.'.format(path))
        else:
            raise Exception('Provide the absolute path.')


class Photo(File):
    acceptable_file_types = ['jpg', 'nef', 'jpeg']
    def __init__(self, path):
        from exifread import process_file
        try:
            super(Photo, self).__init__(path)
            #File.__init__(self, path)
        except FileTypeError:
            raise PhotoTypeError('File is not an accepted photo.')
        self.meta_data = process_file(open(self.path, 'rb'))
        if 'EXIF DateTimeOriginal' in self.meta_data:
            self.creation_date = self.meta_data['EXIF DateTimeOriginal'].values
        elif 'Image DateTime' in self.meta_data:
            self.creation_date = self.meta_data['Image DateTime'].values



class Video(File):
    acceptable_file_types = ['mov', 'mp4', 'mkv', 'm4v', 'avi']
    def __init__(self, path):
        try:
            super(Video, self).__init__(path)
        except FileTypeError:
            raise VideoTypeError('File is not an accepted video.')


class Trash(File):
    acceptable_file_types = None
    def __init__(self, path):
        super(Trash, self).__init__(path)
        self.type = 'trash'
