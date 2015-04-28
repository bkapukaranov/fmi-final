__author__ = 'Borislav Kapukaranov'

import review_util

INPUT_BASE = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/data/raw_reviews'
INPUT = ['cinexio_movie_reviews_filtered.tsv', 'cinexio_movie_reviews_03-16.tsv']

if __name__ == '__main__':
    review_util.save_lexicon(INPUT_BASE, INPUT)