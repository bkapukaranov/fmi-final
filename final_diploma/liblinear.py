__author__ = 'inspir3d'

import codecs
import math
from alphabet_detector import AlphabetDetector
import review_util

INPUT_BASE = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/data/raw_reviews'
#INPUT = ['cinexio_movie_reviews_filtered.tsv', 'cinexio_movie_reviews_03-16.tsv']  # train data
INPUT = ['cinexio_movie_reviews_11_04.tsv']  # test data
LEXICON_IN_BASE = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/data'
LEXICON_POSITIVE = 'positive.txt'
LEXICON_NEGATIVE = 'negative.txt'
OUTPUT_BASE = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/data'
OUTPUT = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/data/cinexio_movie_reviews_test.tsv'
TSV_SEPARATOR = "\t"
FILE_SEPARATOR = "/"
NEGATIVE_BOUNDARY = 2.5
POSITIVE_BOUNDARY = 3.5


def build_liblinear_vectors(input_base, input):
    movies = review_util.get_movies_as_dict(input_base, input)

    positive = {}
    with codecs.open(LEXICON_IN_BASE + FILE_SEPARATOR + LEXICON_POSITIVE, 'r', encoding='utf-8') as pos:
        for line in pos:
            parts = line.split(',')
            if len(parts) != 2:
                continue
            positive[parts[0]] = parts[1]

    negative = {}
    with codecs.open(LEXICON_IN_BASE + FILE_SEPARATOR + LEXICON_NEGATIVE, 'r', encoding='utf-8') as neg:
        for line in neg:
            parts = line.split(',')
            if len(parts) != 2:
                continue
            negative[parts[0]] = parts[1]

    print len(positive)
    print len(negative)

    # class 1:positive_score 2:negative_score
    with open(OUTPUT_BASE + FILE_SEPARATOR + 'testch.txt', 'w') as out:
        for movie_name in movies:
            for review_pair in movies[movie_name][1]:
                review_text = review_pair[0]
                review_rating = float(review_pair[1])

                tokens = review_text.replace(':)', '') \
                    .replace('.', '') \
                    .replace(',', '') \
                    .replace('?', '') \
                    .replace('!', '') \
                    .replace('(', '') \
                    .replace(')', '') \
                    .replace('--', '-') \
                    .replace('"', '') \
                    .lower().split(" ")

                positive_score = 0.0
                negative_score = 0.0
                for token in tokens:
                    if token in positive:
                        positive_score += float(positive[token])
                    if token in negative:
                        negative_score += float(negative[token])

                vector_class = 'b'
                if review_rating > POSITIVE_BOUNDARY:
                    vector_class = 'a'
                if review_rating < NEGATIVE_BOUNDARY:
                    vector_class = 'c'

                out.write(vector_class + ' ' + '1:' + str(positive_score) + ' 2:' + str(negative_score) + '\n')






if __name__ == '__main__':
    build_liblinear_vectors(INPUT_BASE, INPUT)
