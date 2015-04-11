__author__ = 'Borislav Kapukaranov'

import codecs
from alphabet_detector import AlphabetDetector

REVIEWS_FILTERED_TSV = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/cinexio_movie_reviews_filtered.tsv'
REVIEWS_TSV = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/cinexio_movie_reviews.tsv'

INPUT_BASE = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/data/raw_reviews'
INPUT = ['cinexio_movie_reviews.tsv']
OUTPUT = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/data/cinexio_movie_reviews_filtered.tsv'

SEPARATOR = "\t"
movie_total = 0
reviews_total = 0

# Filters only BG movies

if __name__ == '__main__':
    alphabet_detector = AlphabetDetector()

    with codecs.open(REVIEWS_TSV, 'r', encoding="utf-8") as f:
        movie_name = 'null'
        cinexio_rating = 'null'
        cinexio_url = 'null'
        imdb_url = 'null'
        imdb_rating = 'null'

        current = list()

        for line in f:
            clean_line = line.strip().split(SEPARATOR)
            if len(clean_line) > 2:
                # save old movie if it has any bg reviews
                if len(current) > 0:
                    with codecs.open(REVIEWS_FILTERED_TSV, 'a', encoding="utf-8") as filtered:
                        filtered.write(movie_name + SEPARATOR + cinexio_rating + SEPARATOR + cinexio_url + SEPARATOR + imdb_url + SEPARATOR + imdb_rating)
                        filtered.write('\n')
                        filtered.write(str(len(current)))
                        filtered.write('\n')
                        for pair in current:
                            filtered.write(pair[0] + SEPARATOR + str(pair[1]))
                            filtered.write('\n')
                    movie_total += 1
                    reviews_total += len(current)
                # read next one
                movie_name = clean_line[0]
                cinexio_rating = clean_line[1]
                cinexio_url = clean_line[2]
                imdb_url = clean_line[3]
                imdb_rating = clean_line[4]
                current = list()
            if len(clean_line) == 2:
                review_text = clean_line[0]
                review_rating = clean_line[1]
                if alphabet_detector.is_cyrillic(review_text):
                    current.append((review_text, review_rating))
    print movie_total
    print reviews_total
    print "done"
