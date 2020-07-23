
import gen_world_ca
import sys
import os
from os.path import basename
from zipfile import ZipFile

def is_world(s):
    return '.world' in s

def is_grid(s):
    return 'grid_' in s

def is_difficulty(s):
    return 'difficulty_' in s

def zipFilesInDir(dirName, zipFileName, filter):
    # create ZipFile object
    with ZipFile(zipFileName, 'w') as zipObj:
        # iterate over files in directory
        for folderName, subfolders, filenames in os.walk(dirName):
            for filename in filenames:
                if filter(filename):
                    # create complete filepath of file in directory
                    filePath = os.path.join(folderName, filename)
                    zipObj.write(filePath, basename(filePath))

def main():
    smooths = 5
    fillPct = 0.35
    showHeatMap = 0

    # generate worlds
    for i in range(2):
      gen_world_ca.main(i)

    # get current directory
    curr_dir = os.getcwd()
    print(curr_dir)

    # zip files
    zipFilesInDir(curr_dir, 'sampleWorlds.zip', is_world)
    zipFilesInDir(curr_dir, 'sampleGrids.zip', is_grid)
    zipFilesInDir(curr_dir, 'sampleDiffs.zip', is_difficulty)


if __name__ == "__main__":
    main()
