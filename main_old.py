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
from structure import Photo, Video, Trash
from errors import *
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname)s: %(message)s')

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)

log.addHandler(ch)



SORTED_FOLDER = 'D:\\Stephany\\Stephanys Pictures\\Sorted'
DIR_TO_SEARCH = 'D:\\Stephany\\Stephanys Pictures\\To be sorted'
RECURSIVE_DIR_SEARCH = False
GLOBAL_COPY = False
GLOBAL_MOVE = True
WANTED_CAMERA_MODELS = ['nikon', 'samsung', 'motorola', '*']
DEBUG = True


def load_files_from_dir(dir, recursive=False):
    import os
    photo_list = []
    video_list = []
    trash_list = []
    if recursive:
        for dirName, subdirList, fileList in os.walk(dir):
            if SORTED_FOLDER in dirName:
                logging.debug('Skipping Sorted folder')
                continue
            for file in fileList:
                fp = os.path.join(dirName, file)
                try:
                    p = Photo(fp)
                    photo_list.append(p)
                except FileTypeError:
                    log.debug('{} - file type error.'.format(file))
                except Exception:
                    pass
    else:
        for file in os.listdir(dir):
            fp = os.path.join(dir, file)
            fp = os.path.abspath(path=fp)
            if not os.path.isfile(fp):
                continue
            extension = file.split('.')[-1]
            extension = extension.lower()
            if extension in Photo.acceptable_file_types:
                print fp
                yield Photo(fp)
                #photo_list.append(Photo(fp))
            elif extension in Video.acceptable_file_types:
                yield Video(fp)
                #video_list.append(Video(fp))
            else:
                continue



def find_similar_media_file(dirName, media_fileName, exiftags):
    """
    :param dirName: directory to search
    :param media_fileName: orginal media_files name
    :param exiftags: tags belonging to orginal media_file
    :return: the name of the same media_file under a different (but similar) name
    """
    import os
    import exifread
    for files in os.listdir(dirName):
        baseName, fileExt = media_fileName.split('.')
        if files[-len(fileExt):] != fileExt:
            continue
        if baseName.count(' ('):
            baseName = baseName.split(' (')[0]
        if baseName in files:
            f = open(os.path.join(dirName, files), 'rb')
            searchPhotoTags = exifread.process_file(f, details=False)
            if searchPhotoTags['EXIF DateTimeOriginal'].values == exiftags['EXIF DateTimeOriginal'].values:
                return files
    return False


def sort_file_by_date(*args, **kwargs):
    import shutil
    import os
    import calendar
    OVERWRITE_SAME_MEDIA = False
    RENAME_MEDIA = True
    DELETE_SAME_MEDIA = True
    for media_file in args:
        if media_file.type == 'Trash':
            continue
        #################
        # Validates the media_files came from a trusted source (the Nikon, phone, or post-edited media_fileshop)
        #################
        if media_file.type == 'Photo':
            if 'Image Make' in media_file.meta_data:
                # Make sure the picture was taken by a trusted source
                if media_file.meta_data['Image Make'].values.lower().split(' ')[0] not in WANTED_CAMERA_MODELS \
                        and '*' not in WANTED_CAMERA_MODELS:
                    log.debug('{} not processed due to Image Make.'.format(media_file.name))
                    continue
            elif 'Image Software' in media_file.meta_data and '*' not in WANTED_CAMERA_MODELS:
                # If there's not source identifier, check and see if it was edited by media_fileshop
                if 'media_fileshop' not in media_file.meta_data['Image Software'].values.lower():
                    log.debug('{} not processed due to Image Software.'.format(media_file.name))
                    continue
        #################
        # End media_file source validation
        #################

        year = media_file.creation_date.split(':')[0]
        month = calendar.month_name[int(media_file.creation_date.split(':')[1])]
        file_path = os.path.join(SORTED_FOLDER, year, month)
        existing_file_path = os.path.join(file_path, media_file.name)
        copied = False
        if not os.path.exists(file_path):
            # Checks to see if there is a file already in the sorted folder
            os.makedirs(os.path.join(SORTED_FOLDER, year, month))
        try:
            user_input = 'n'
            user_input_new = 'n'
            if os.path.isfile(existing_file_path):
                # Check and see if this file already exists.
                log.debug('{}: {} exists.'.format(os.path.isfile(existing_file_path), existing_file_path))
                if media_file.type == 'Photo':
                    try:
                        new_media_file_tags = Photo(existing_file_path)
                        log.debug('Opening existing pictures EXIF tags.')
                    except IndexError:
                        log.debug('Error on {}'.format(existing_file_path))
                        continue
                if media_file.type == 'Video':
                    try:
                        new_media_file_tags = Video(existing_file_path)
                        log.debug('Opening existing video file.')
                    except IndexError:
                        log.debug('Error on {}'.format(existing_file_path))
                        continue
                if new_media_file_tags.creation_date == media_file.creation_date and new_media_file_tags.hash == media_file.hash:
                # Add additional checks to this IF statement for better confirmation theyre the same; maybe the hash
                # -- implemented 23July17
                    log.debug('SAME FILE: {}'.format(media_file.path))
                    log.debug('SAME FILE: {}'.format(existing_file_path))
                    if OVERWRITE_SAME_MEDIA:
                        user_input = raw_input('Look like the same media_file should I overwrite? [Y|N]')
                    else:
                        log.debug('Not overwriting media_file. File already exists in folder under a different name.')
                        if DELETE_SAME_MEDIA:
                            log.debug('Deleteing {}'.format(media_file.path))
                            os.remove(media_file.path)
                else:
                    # If names are the same then check all names that are similar to see if
                    #   the file was saved under a different name
                    log.debug('DIFFERENT FILE: {}'.format(existing_file_path))
                    found_similar = find_similar_media_file(file_path, media_file.name, media_file.meta_data)
                    if found_similar:
                        log.debug('Found similar media_file under a different name ({}). Skipping'.format(found_similar))
                        continue
                    else:
                        if RENAME_MEDIA:
                            user_input_new = 'y'
                        else:
                            user_input_new = raw_input(
                                'Looks like a different media_file should I write with a new name? [Y|N]')
                if user_input.lower() == 'n' and user_input_new.lower() == 'n':
                    continue
                elif user_input.lower() == 'y':
                    # Overwrite media_file that already exists under the same name
                    log.debug('Overwriting existing file for {}'.format(media_file.path))
                    if kwargs['copy']:
                        shutil.copy2(media_file.path, file_path)
                        copied = True
                    elif kwargs['move']:
                        shutil.move(media_file.path, file_path)
                        moved = True
                elif user_input_new.lower() == 'y':
                    # The name of the media_file exists, but it is not the same media_file that needs to be written
                    #   Will increment the name to save
                    new_name = os.path.join(file_path, media_file.name)
                    count = 0
                    while os.path.isfile(new_name):
                        new_name = os.path.join(file_path,
                                                media_file.name.replace('.' + media_file.file_extension, '') + \
                                                ' ({}).{}'.format(count, media_file.file_extension))
                        count += 1
                    log.debug('Saving {} as {}'.format(media_file.path, new_name))
                    if kwargs['copy']:
                        shutil.copy2(media_file.path, new_name)
                        copied = True
                    elif kwargs['move']:
                        log.debug('Original Photo {}'.format(media_file.path))
                        shutil.move(media_file.path, new_name)
                        moved = True
            else:
                # Sorted folder does not exists. Copy or Move the file
                if kwargs['copy']:
                    shutil.copy2(media_file.path, file_path)
                    log.info('Copied {}'.format(media_file))
                    copied = True
                elif kwargs['move']:
                    log.debug('Original Photo {}'.format(media_file.path))
                    shutil.move(media_file.path, file_path)
                    log.info('Moved {} to {}'.format(media_file, file_path or new_name))
                    moved = True
        except IOError as e:
            if 'Permission denied' in e.message:
                log.warning('Permission denied on {}'.format(media_file))
            else:
                pass
            pass


if __name__ == '__main__':
    import time
    num_of_photos = 0
    start_time = time.time()
    for f in load_files_from_dir(DIR_TO_SEARCH, recursive=RECURSIVE_DIR_SEARCH):
        sort_file_by_date(f, copy=GLOBAL_COPY, move=GLOBAL_MOVE)
        num_of_photos += 1
    sleep(1)
    total_time = time.time() - start_time
    print('{} photos processed in {} seconds.'.format(num_of_photos, total_time))
    if total_time != 0:
        print('It took an average of {} seconds per photo.'.format(total_time/num_of_photos))
    raw_input("Press Enter to exit.")
