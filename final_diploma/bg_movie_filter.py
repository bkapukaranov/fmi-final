__author__ = 'Borislav Kapukaranov'

import codecs
from alphabet_detector import AlphabetDetector

REVIEWS_FILTERED_TSV = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/cinexio_movie_reviews_full_filtered.tsv'
REVIEWS_TSV = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/cinexio_movie_reviews_full.tsv'

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
        director = 'null'
        actors = 'null'
        country = 'null'
        genres = 'null'
        length = 'null'

        current = list()

        for line in f:
            clean_line = line.strip().split(SEPARATOR)
            if len(clean_line) == 10:
                # save old movie if it has any bg reviews
                if len(current) > 0:
                    with codecs.open(REVIEWS_FILTERED_TSV, 'a', encoding="utf-8") as filtered:
                        filtered.write(movie_name + SEPARATOR
                                       + cinexio_rating + SEPARATOR
                                       + cinexio_url + SEPARATOR
                                       + imdb_url + SEPARATOR
                                       + imdb_rating + SEPARATOR
                                       + director + SEPARATOR
                                       + actors + SEPARATOR
                                       + country + SEPARATOR
                                       + genres + SEPARATOR
                                       + length + SEPARATOR)
                        filtered.write('\n')
                        filtered.write(str(len(current)))
                        filtered.write('\n')
                        for tuple in current:
                            filtered.write(tuple[0] + SEPARATOR + tuple[1] + SEPARATOR + str(tuple[2]) + SEPARATOR + str(tuple[3]))
                            filtered.write('\n')
                    movie_total += 1
                    reviews_total += len(current)
                # read next one
                movie_name = clean_line[0]
                cinexio_rating = clean_line[1]
                cinexio_url = clean_line[2]
                imdb_url = clean_line[3]
                imdb_rating = clean_line[4]
                director = clean_line[5]
                actors = clean_line[6]
                country = clean_line[7]
                genres = clean_line[8]
                length = clean_line[9]
                current = list()
            if len(clean_line) == 4:
                reviewer_name = clean_line[0]
                review_text = clean_line[1]
                review_rating = clean_line[2]
                review_date = clean_line[3][:-1]

                if alphabet_detector.is_cyrillic(review_text):
                    current.append((reviewer_name, review_text, review_rating, review_date))
    print movie_total
    print reviews_total
    print "done"
