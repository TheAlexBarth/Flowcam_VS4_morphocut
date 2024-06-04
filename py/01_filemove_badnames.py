import os
import utilities as utils

big_dir = '/Users/planktonperson/Data/Buskey_FC/SWMP_2014-15_badnames'

if not os.path.exists(os.path.join(big_dir, 'raw')):
    os.mkdir(os.path.join(big_dir, 'raw'))

dir_names = [d for d in os.listdir(big_dir) if os.path.isdir(os.path.join(big_dir, d))] # add all directories to this list
dir_names = [d for d in dir_names if d not in ['metadata','raw','ecotaxa']]


for dir in dir_names:
    utils.move_files(os.path.join(big_dir, dir), os.path.join(big_dir, 'raw'))