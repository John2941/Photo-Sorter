# Photo-Sorter
Sorts photos placed into a specified directory by date. Edit

```
usage: main.py [-h] --sort SORTED_FOLDER [--recursive] --media DIR_TO_SEARCH
               [--debug] [--info] [--overwrite] [--cleanup] [--manual-rename]
               (--copy | --move)

optional arguments:
  -h, --help            show this help message and exit
  --sort SORTED_FOLDER  Folder to place sorted files.
  --recursive           Recursively search the --media_folder.
  --media DIR_TO_SEARCH
                        Folder to search for file to sort.
  --debug               Display debugging messages.
  --info                Display informational messages.
  --overwrite           Will overwrite copies of the file if they're found in
                        the --sort folder.
  --cleanup             Will delete media files from --media folder after it
                        transfers it to the --sort folder.
  --manual-rename       Will prompt the user to specific a new name for a
                        file, if the name already exists and its not a
                        duplicate of the file.
  --copy                Copy files instead of moving them.
  --move                Move files instead of copying them.
```


Photos and Videos will be placed into a file structure like this:
```
2015
|_ December
  |_ 1.jpg
|_ October
  |_ 24.jpg
2016
|_ April
  |_ fun.jpeg
  |_ i like ice cream.nef
```