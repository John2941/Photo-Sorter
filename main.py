"""
@Project Name - main
@author - Johnathan
@date - 11/26/2016
@time - 6:06 PM


Set the global variables below and run script.
Be sure to kow the acceptable filetypes.
"""
import time
import os
from structure import Photo, Video, Trash
import logging
import shutil
import argparse

WANTED_CAMERA_MODELS = ['nikon', 'samsung', 'motorola', '*']




def load_files_from_dir(dir, recursive=False):
    """
    :param dir: directory listing to process to sent to process_files()
    :param recursive: boolean: should this recursively check the dir parameter
    :return: a list of absolute file paths
    """
    import os
    files = []

    for root_dir, sub_dir, file_list in os.walk(dir):
        for file in file_list:
            full_fp = os.path.join(root_dir, file)
            files.append(full_fp)
        if not recursive:
            break

    return files


def process_files(dir_list):
    """
    :param dir_list: a list of files to process into Photo, Video, or Trash class
    :return: a Photo or Video class object
    """

    for abs_path in dir_list:
        assert os.path.abspath(path=abs_path)
        filename, file_extension = os.path.splitext(abs_path)
        file_extension = file_extension[1:]  # Get rid of the period
        if file_extension in Photo.acceptable_file_types:
            print abs_path
            yield Photo(abs_path)
        elif file_extension in Video.acceptable_file_types:
            print abs_path
            yield Video(abs_path)
        else:
            continue  # Add trash class in here




def find_similar_media_file(dirName, media_fileName, exiftags):
    """
    :param dirName: directory to search
    :param media_fileName: original media_files name
    :param exiftags: tags belonging to original media_file
    :return: the name of the same media_file under a different (but similar) name
    """
    import os
    import exifread
    for files in os.listdir(dirName):
        orig_file_extension = media_fileName.split('.')[-1]
        orig_filename = '.'.join(media_fileName.split('.')[:-1])
        filename, file_extension = os.path.splitext(files)
        file_extension = file_extension[1:]

        if orig_filename not in filename:
            continue

        abs_path = os.path.join(dirName, files)
        with open(abs_path, 'rb') as binary_file:
            searchPhotoTags = exifread.process_file(binary_file, details=False)
            # Now lets check and see if the DateTimeOriginal metadata matches
            try:
                if searchPhotoTags['EXIF DateTimeOriginal'].values == exiftags['EXIF DateTimeOriginal'].values:
                    # They are the same
                    return files
            except KeyError:
                # Gonna have to assume they are different
                continue
    return False


def increment_filename(dirName, media_fileName):
    """
    :param dirName: directory to search
    :param media_fileName: original media_files name
    :return: new absolute path with an incremented filename
    """
    import os
    for i in xrange(1, 10000):
        orig_file_extension = media_fileName.split('.')[-1]
        orig_filename = '.'.join(media_fileName.split('.')[:-1])
        new_filename = '{} ({}).{}'.format(orig_filename, i, orig_file_extension)
        new_abs_path = os.path.join(dirName, new_filename)
        if not os.path.exists(new_abs_path):
            return new_abs_path



def valid_photo_source(photo):
    """
    Why did I add this? idk ... seems like a good idea at first, but now is kinda stupid
    Validates a photo came from a trusted source (the Nikon, phone, or post-edited photo)
    :param photo: Photo class object
    :return: boolean; True if photo from a valid source
    """
    if 'Image Make' in photo.meta_data:
        # Make sure the picture was taken by a trusted source
        if photo.meta_data['Image Make'].values.lower().split(' ')[0] not in WANTED_CAMERA_MODELS \
                and '*' not in WANTED_CAMERA_MODELS:
            log.debug('{} not processed due to Image Make.'.format(photo.name))
            return False
    elif 'Image Software' in photo.meta_data and '*' not in WANTED_CAMERA_MODELS:
        # If there's not source identifier, check and see if it was edited by media_fileshop
        if 'media_fileshop' not in photo.meta_data['Image Software'].values.lower():
            log.debug('{} not processed due to Image Software.'.format(photo.name))
            return False
    return True


def transfer_file(src, dst):
    """
    :param src: absolute file path for the source file
    :param dst: absolute file path where you want the file transfered
    :return: noffin
    """
    if arguments.copy:
        shutil.copy2(src, dst)
        if arguments.cleanup:
            # Deleting the duplicate media file from the --media folder
            log.debug('Deleting {}'.format(src))
            os.remove(src)
    elif arguments.move:
        shutil.move(src, dst)


def sort_file_by_date(files):
    import os
    import calendar
    for media_file in files:
        if media_file.type == 'Trash':
            continue

        if media_file.type == 'Photo' and not valid_photo_source(media_file):
            # Validates a photo came from a trusted source (the Nikon, phone, or post-edited photo)
            continue

        year = media_file.creation_date.split(':')[0]
        month = calendar.month_name[int(media_file.creation_date.split(':')[1])]
        file_path = os.path.join(arguments.sorted_folder, year, month)
        existing_file_path = os.path.join(file_path, media_file.name)
        if not os.path.exists(file_path):
            # Checks to see if there is a file already in the sorted folder
            os.makedirs(os.path.join(arguments.sorted_folder, year, month))
        try:
            if os.path.isfile(existing_file_path):
                # Check and see if this file already exists.
                # This path means there's already a file with the same name.
                log.debug('{}: {} exists.'.format(os.path.isfile(existing_file_path), existing_file_path))
                if media_file.type == 'Photo':
                    try:
                        new_media_file_tags = Photo(existing_file_path)
                        log.debug('Opening existing pictures EXIF tags.')
                    except IndexError:
                        log.debug('Error on {}'.format(existing_file_path))
                        continue
                elif media_file.type == 'Video':
                    try:
                        new_media_file_tags = Video(existing_file_path)
                        log.debug('Opening existing video file.')
                    except IndexError:
                        log.debug('Error on {}'.format(existing_file_path))
                        continue
                if new_media_file_tags.hash() == media_file.hash():
                    # Exact same media file found.
                    log.debug('SAME FILE: {}'.format(media_file.path))
                    log.debug('SAME FILE: {}'.format(existing_file_path))
                    if arguments.overwrite:
                        transfer_file(media_file.path, file_path)
                    else:
                        # Not going to overwrite the same file in the --sort folder
                        log.debug('Not overwriting media_file. File already exists in folder under a different name.')
                        if arguments.cleanup:
                            # Deleting the duplicate media file from the --media folder
                            log.debug('Deleteing {}'.format(media_file.path))
                            os.remove(media_file.path)
                    continue
                else:
                    # The new media file to be copied/moved has the same name as another file in the --sort folder, but
                    #       is not the exact match. Will need to increment the name. We will check any other media files
                    #       that have the same root name, but have an increment. i.e., beachphoto (2).jpg
                    log.debug('DIFFERENT FILE: {}'.format(existing_file_path))
                    found_similar = find_similar_media_file(file_path, media_file.name, media_file.meta_data)
                    if found_similar:
                        # Found the same file under a different incremented name
                        log.debug('Found similar media_file under a different name ({}). Skipping'.format(found_similar))
                        if arguments.manual_rename:
                            while True:
                                new_file_name = raw_input('What would you like to rename the file? ')

                                new_file_name = '{}.{}'.format(new_file_name, media_file.file_extension)
                                new_abs_path = os.path.join(file_path, new_file_name)
                                if os.path.exists(new_abs_path):
                                    print('Filename already exists. Pick another.')
                                else:
                                    break
                            transfer_file(media_file.path, new_abs_path)
                        elif arguments.overwrite:
                            transfer_file(media_file.path, found_similar)
                        continue
                    else:
                        # All incremented names were not a copy
                        if arguments.manual_rename:
                            while True:
                                new_file_name = raw_input('What would you like to rename the file? ')

                                new_file_name = '{}.{}'.format(new_file_name, media_file.file_extension)
                                new_abs_path = os.path.join(file_path, new_file_name)
                                if os.path.exists(new_abs_path):
                                    print('Filename already exists. Pick another.')
                                else:
                                    break
                            transfer_file(media_file.path, new_abs_path)
                        else:
                            #  Increment the name and save
                            incremented_abs_path = increment_filename(file_path, media_file.name)
                            transfer_file(media_file.path, incremented_abs_path)
            else:
                # Media filename to be copied or moved does not exist in the --sort folder. Nothing fancy
                #    needs to be done. So copy or move the file
                transfer_file(media_file.path, file_path)

        except IOError as e:
            if 'Permission denied' in e.message:
                log.warning('Permission denied on {}'.format(media_file))
            pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--sort", action='store', dest='sorted_folder', required=True, help="Folder to place sorted files.")
    parser.add_argument('--recursive', action='store_true', dest='recursive_dir', help='Recursively search the --media_folder.')
    parser.add_argument('--media', action='store', dest='dir_to_search', required=True, help='Folder to search for file to sort.')
    parser.add_argument('--debug', action='store_true', dest='debug', help='Display debugging messages.')
    parser.add_argument('--info', action='store_true', dest='info', help='Display informational messages.')

    parser.add_argument('--overwrite', action='store_true', dest='overwrite', help='Will overwrite copies of the file if they\'re found in the --sort folder.')
    parser.add_argument('--cleanup', action='store_true', dest='cleanup', help='Will delete media files from --media folder after it transfers it to the --sort folder.')
    parser.add_argument('--manual-rename', action='store_true', dest='manual_rename', help='Will prompt the user to specific a new name for a file, if the name already exists and its not a duplicate of the file.')
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--copy', action='store_true', dest='copy', help='Copy files instead of moving them.')
    group.add_argument('--move', action='store_true', dest='move', help='Move files instead of copying them.')

    arguments = parser.parse_args()

    log = logging.getLogger(__name__)
    if arguments.debug:
        log.setLevel(logging.DEBUG)
    elif arguments.info:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.NOTSET)
    formatter = logging.Formatter('%(levelname)s: %(message)s')

    ch = logging.StreamHandler()
    if arguments.debug:
        ch.setLevel(logging.DEBUG)
    elif arguments.info:
        ch.setLevel(logging.INFO)
    else:
        ch.setLevel(logging.NOTSET)
    ch.setFormatter(formatter)
    log.addHandler(ch)

    num_of_photos = 0
    start_time = time.time()

    unprocessed_files = load_files_from_dir(arguments.dir_to_search, recursive=arguments.recursive_dir)

    for f in process_files(unprocessed_files):
        sort_file_by_date(f)
        num_of_photos += 1

    total_time = time.time() - start_time
    print('{} photos processed in {} seconds.'.format(num_of_photos, total_time))
    if total_time != 0:
        avg_time = 0 if num_of_photos == 0 else total_time / num_of_photos
        print('It took an average of {} seconds per photo.'.format(avg_time))
    raw_input("Press Enter to exit.")
