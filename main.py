"""
@Project Name - main
@author - Johnathan
@date - 11/26/2016
@time - 6:06 PM


Set the global variables below and run script.
Be sure to kow the acceptable filetypes.
"""
from time import sleep
import time
import os
import hashlib

SORTED_FOLDER = 'D:\\Stephany\\Stephanys Pictures\\Sorted'
DIR_TO_SEARCH = 'D:\\Stephany\\Stephanys Pictures\\To be sorted'
RECURSIVE_DIR_SEARCH = True
GLOBAL_COPY = False
GLOBAL_MOVE = True
CAMERA_NAME = 'NIKON'


class File(object):
    def __init__(self, path):
        self.path = self._verify(path)
        self.stat = os.stat(self.path)
        self.file_extension = os.path.splitext(self.path)[1][1:]
        self.name = os.path.basename(self.path)
        self.creation_date = time.strftime("%m/%d/%Y %H:%M:%S", time.localtime(self.stat.st_ctime))
        self.last_modified = time.strftime("%m/%d/%Y %H:%M:%S", time.localtime(self.stat.st_mtime))

    def __repr__(self):
        return self.name

    @staticmethod
    def hash(self, path):
        hash_md5 = hashlib.md5()
        with open(path, "rb") as f:
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
                            raise Exception('{} is not an acceptable file extension'.format(file_ext))
                    else:
                        return path
            else:
                raise Exception('{} is not a file.'.format(path))
        else:
            raise Exception('Provide the absolute path.')


class Photo(File):
    def __init__(self, path):
        import exifread
        self.acceptable_file_types = ['jpg', 'nef', 'jpeg']
        File.__init__(self, path)
        self.photo_data = exifread.process_file(open(self.path, 'rb'))
        self.exif_photo_taken_date = self.photo_data['EXIF DateTimeOriginal'].values


class Video(File):
    def __init__(self, path):
        self.acceptable_file_types = ['mov']
        File.__init__(self, path)


class Trash(File):
    def __init__(self, path):
        self.acceptable_file_types = None
        File.__init__(self, path)


def load_files_from_dir(dir, recursive=False):
    import os
    photos = []
    if recursive:
        for dirName, subdirList, fileList in os.walk(dir):
            pl = []
            if SORTED_FOLDER in dirName:
                print 'Skipping Sorted folder'
                continue
            for file in fileList:
                fp = os.path.join(dirName, file)
                # print fp
                try:
                    #
                    sort_photos_by_date([Photo(fp)], copy=GLOBAL_COPY, move=GLOBAL_MOVE)
                except Exception:
                    pass
            if pl:
                print '{} photos found.'.format(len(pl))
                sort_photos_by_date(pl, copy=GLOBAL_COPY, move=GLOBAL_MOVE)
    else:
        for file in os.listdir(dir):
            try:
                photos.append(Photo(os.path.join(dir, file)))
            except Exception:
                pass
    return photos


def find_similar_photo(dirName, photoName, exiftags):
    """
    :param dirName: directory to search
    :param photoName: orginal photos name
    :param exiftags: tags belonging to orginal photo
    :return: the name of the same photo under a different (but similar) name
    """
    import os
    import exifread
    for files in os.listdir(dirName):
        baseName, fileExt = photoName.split('.')
        if files[-len(fileExt):] != fileExt:
            continue
        if baseName.count(' ('):
            baseName = baseName.split(' (')[0]
        if baseName in files:
            searchPhotoTags = exifread.process_file(open(os.path.join(dirName, files), 'rb'))
            if searchPhotoTags['EXIF DateTimeOriginal'].values == exiftags['EXIF DateTimeOriginal'].values:
                return files
    return False


def sort_photos_by_date(photoList, copy=True, move=False):
    import shutil
    import os
    import calendar
    import exifread
    DEBUG = True
    DEBUG_OVERWRITE = False
    DEBUG_RENAME = True
    OVERWRITE_SAME_PHOTO = False
    RENAME_PHOTOS = True
    DELETE_SAME_PHOTO = True
    for photo in photoList:
        if 'Image Make' in photo.photo_data.keys() and CAMERA_NAME in photo.photo_data['Image Make'].values:
            year = photo.exif_photo_taken_date.split(':')[0]
            month = calendar.month_name[int(photo.photo_data['EXIF DateTimeOriginal'].values.split(':')[1])]
            file_path = os.path.join(SORTED_FOLDER, year, month)
            new_photo_path = os.path.join(file_path, photo.name)
            copied = False
            if not os.path.exists(file_path):
                os.makedirs(os.path.join(SORTED_FOLDER, year, month))
            try:
                user_input = 'n'
                user_input_new = 'n'
                if DEBUG:
                    print '{}: {} exists.'.format(os.path.isfile(new_photo_path), new_photo_path)
                if os.path.isfile(new_photo_path):
                    try:
                        new_photo_tags = exifread.process_file(open(new_photo_path), 'rb')
                        if DEBUG:
                            print 'Opening existing pictures EXIF tags.'
                    except IndexError:
                        if DEBUG:
                            print 'Error on {}'.format(new_photo_path)
                        continue
                    if new_photo_tags['EXIF DateTimeOriginal'].values == photo.photo_data[
                        'EXIF DateTimeOriginal'].values:
                        if DEBUG_OVERWRITE or DEBUG:
                            print 'SAME PHOTO: {}'.format(photo.path)
                            print 'SAME PHOTO: {}'.format(new_photo_path)
                        if OVERWRITE_SAME_PHOTO:
                            user_input = raw_input('Look like the same photo should I overwrite? [Y|N]')
                        else:
                            if DEBUG or DEBUG_OVERWRITE or DEBUG_RENAME:
                                print 'Not overwriting photo. Photo already exists in folder under a different name.'
                                if DELETE_SAME_PHOTO:
                                    print 'Deleteing {}'.format(photo.path)
                            if DELETE_SAME_PHOTO:
                                os.remove(photo.path)
                    else:
                        # If names are the same then check all names that are similar to see if
                        #   the file was saved under a different name
                        if DEBUG or DEBUG_RENAME:
                            print 'DIFFERENT PHOTO: {}'.format(new_photo_path)
                        found_similar = find_similar_photo(file_path, photo.name, photo.photo_data)
                        if found_similar:
                            if DEBUG or DEBUG_OVERWRITE:
                                print 'Found similar photo under a different name ({}). Skipping'.format(found_similar)
                                continue
                        else:
                            if RENAME_PHOTOS:
                                user_input_new = 'y'
                            else:
                                user_input_new = raw_input(
                                    'Looks like a different photo should I write with a new name? [Y|N]')
                    if user_input.lower() == 'n' and user_input_new.lower() == 'n':
                        continue
                    elif user_input.lower() == 'y':
                        # Overwrite photo that already exists under the same name
                        if DEBUG or DEBUG_OVERWRITE:
                            print 'Overwriting existing file for {}'.format(photo.path)
                        if copy:
                            shutil.copy2(photo.path, file_path)
                            copied = True
                        elif move:
                            shutil.move(photo.path, file_path)
                            moved = True
                    elif user_input_new.lower() == 'y':
                        # The name of the photo exists, but it is not the same photo that needs to be written
                        #   Will increment the name to save
                        new_name = os.path.join(file_path, photo.name)
                        count = 0
                        while os.path.isfile(new_name):
                            new_name = os.path.join(file_path,
                                                    photo.name.replace('.' + photo.file_extension, '') + \
                                                    ' ({}).{}'.format(count, photo.file_extension))
                            count += 1
                        if DEBUG or DEBUG_RENAME:
                            print 'Saving {} as {}'.format(photo.path, new_name)
                        if copy:
                            shutil.copy2(photo.path, new_name)
                            copied = True
                        elif move:
                            if DEBUG_RENAME:
                                print 'Original Photo {}'.format(photo.path)
                            shutil.move(photo.path, new_name)
                            moved = True
                else:
                    if copy:
                        shutil.copy2(photo.path, file_path)
                        copied = True
                    elif move:
                        if DEBUG_RENAME:
                            print 'Original Photo {}'.format(photo.path)
                        shutil.move(photo.path, file_path)
                        moved = True
            except IOError as e:
                if 'Permission denied' in e.message:
                    print 'Permission denied on {}'.format(photo)
                else:
                    pass
                pass
            if copied and DEBUG:
                print 'Copied {}'.format(photo)
            if moved and DEBUG:
                print 'Moved {} to {}'.format(photo, file_path or new_name)


if __name__ == '__main__':
    load_files_from_dir(DIR_TO_SEARCH, recursive=RECURSIVE_DIR_SEARCH)
    raw_input("Press Enter to exit.")
