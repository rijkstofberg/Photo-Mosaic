#!/bin/python

import os
import sys
import glob
import extract_meta
import mosaic
import pickle


CURRENT_DIR = os.getcwd()
DB_FILE = os.path.join(CURRENT_DIR, 'tiles.pickle')
TILES_DIR = os.path.join(CURRENT_DIR, 'tiles')
SOURCE_DIR = os.path.join(CURRENT_DIR, 'source')
TARGET_DIR = os.path.join(CURRENT_DIR, 'target')
ERRORS = {
    'NO_TILES': 'No tile images in db.',
    'NO_TILES_DIR': 'Missing tiles directory:%s.' %TILES_DIR,
    'NO_SOURCE_DIR': 'Missing source directory:%s.' %SOURCE_DIR,
    'NO_TARGET_DIR': 'Missing target directory:%s.' %TARGET_DIR,
    'NO_SOURCE_PHOTOS': 'No photos to process in:%s.' %SOURCE_DIR,
}


def check_environment(errors, tiles_dir, source_dir, target_dir):
    # check if tiles folder exists
    if not os.path.isdir(tiles_dir):
        errors.append(ERRORS.get('NO_TILES_DIR'))
    # check if source folder exists
    if not os.path.isdir(source_dir):
        errors.append(ERRORS.get('NO_SOURCE_DIR'))
    # check if target folder exists
    if not os.path.isdir(target_dir):
        errors.append(ERRORS.get('NO_TARGET_DIR'))
    return errors

def setup_tile_db(errors, db_file):
    if os.path.isfile(DB_FILE):
        db_file = open(DB_FILE, 'r')
        tiles_db = pickle.load(db_file)
        if len(tiles_db) < 1:
            errors.append(ERRORS.get('NO_TILES'))
    else:
        tiles = glob.glob(os.path.join(TILES_DIR, '*.png'))
        if tiles:
            tiles_db = [
                (tile, extract_meta.extractPhotoInfo(tile)) \
                 for tile in tiles
            ]
            db_file = open(DB_FILE, 'wb')
            pickle.dump(tiles_db, db_file)
        else:
            errors.append(ERRORS.get('NO_TILES'))
    db_file.close()
    return errors, tiles_db


def process_image(errors, tiles_db, SOURCE_DIR, TARGET_DIR):
    photos = glob.glob(os.path.join(SOURCE_DIR, '*.png'))
    if not photos:
        errors.append(ERRORS.get('NO_SOURCE_PHOTOS'))

    for photo in photos:
        pname = photo.split(os.sep)[-1]
        # create Cartesian result
        result = mosaic.createMosaic(tiles_db, photo)
        result.show()
        file_name = os.path.join(TARGET_DIR, ('result-Cartesian-%s' %pname))
        result.save(file_name, 'PNG')
        # create hex result
        result = mosaic.createMosaicHex(tiles_db, photo)
        result.show()
        file_name = os.path.join(TARGET_DIR, ('result-Hex-%s' %pname))
        result.save(file_name, 'PNG')
    return errors


if __name__ == '__main__':
    errors = []

    # check that we got the necessary data and directories
    errors = check_environment(errors, TILES_DIR, SOURCE_DIR, TARGET_DIR)

    # setup DB with tile details
    errors, tiles_db = setup_tile_db(errors, DB_FILE)

    # process the provided image 
    errors = process_image(errors, tiles_db, SOURCE_DIR, TARGET_DIR)

    if errors:
        for error in errors:
            print error
        sys.exit(1)

    print 'Done'
