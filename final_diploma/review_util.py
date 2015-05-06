__author__ = 'Borislav Kapukaranov'

import codecs
import math
from alphabet_detector import AlphabetDetector

NEGATIVE_BOUNDARY = 2.5
POSITIVE_BOUNDARY = 3.5

INPUT_BASE = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/data/raw_reviews'
INPUT = ['cinexio_movie_reviews_filtered.tsv', 'cinexio_movie_reviews_03-16.tsv']
OUTPUT_BASE = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/data'
OUTPUT = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/data/cinexio_movie_reviews_test.tsv'
TSV_SEPARATOR = "\t"
FILE_SEPARATOR = "/"


def get_movies_as_dict_old(input_base, input):
    movie_to_reviews = dict()

    alphabet_detector = AlphabetDetector()

    for file in input:
        with codecs.open(input_base + FILE_SEPARATOR + file, 'r', encoding="utf-8") as f:
            movie_name = 'null'
            cinexio_rating = 'null'
            cinexio_url = 'null'
            imdb_url = 'null'
            imdb_rating = 'null'

            current = list()

            for line in f:
                clean_line = line.strip().split(TSV_SEPARATOR)
                if len(clean_line) > 2:
                    # collect old movie if it has any bg reviews
                    if len(current) > 0:
                        movie_to_reviews[movie_name] = (
                            movie_name + TSV_SEPARATOR + cinexio_rating + TSV_SEPARATOR + cinexio_url + TSV_SEPARATOR + imdb_url + TSV_SEPARATOR + imdb_rating,
                            set())
                        for pair in current:
                            movie_to_reviews[movie_name][1].add(pair)
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
    return movie_to_reviews


def movies_as_list(input_base, input):
    movie_to_reviews = []

    for file in input:
        with codecs.open(input_base + FILE_SEPARATOR + file, 'r', encoding="utf-8") as f:
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
                clean_line = line.strip().split(TSV_SEPARATOR)
                if len(clean_line) == 10:
                    # collect old movie if it has any bg reviews
                    if len(current) > 0:
                        movie_to_reviews.append({'name': movie_name,
                                                 'cinexio_rating': cinexio_rating,
                                                 'cinexio_url': cinexio_url,
                                                 'imdb_url': imdb_url,
                                                 'imdb_rating': imdb_rating,
                                                 'director': director,
                                                 'actors': actors.split(', '),
                                                 'country': country,
                                                 'genres': genres.split(', '),
                                                 'length': length,
                                                 'reviews': []})
                    for r_dict in current:
                        movie_to_reviews[-1]['reviews'].append(r_dict)
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
                    current.append({'r_name': reviewer_name, 'r_text': review_text, 'r_rating': review_rating, 'r_date': review_date})

    return movie_to_reviews


def build_lexicon_poles(input, input_base):
    movies = get_movies_as_dict_old(input_base, input)
    opinion_border = float(3)
    dictionary = {}
    class_count = {'positive': 0, 'negative': 0, 'neutral': 0}
    review_count = 0
    for movie_name in movies:
        for review_pair in movies[movie_name][1]:
            review_text = review_pair[0]
            review_rating = float(review_pair[1])

            review_count += 1

            if review_rating > opinion_border:
                class_count['positive'] += 1
            else:
                class_count['negative'] += 1

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

            for token in tokens:
                if token in dictionary:
                    tuple = dictionary[token]
                    # total word count
                    new_total = tuple[0] + 1
                    new_positive = tuple[1]
                    new_negative = tuple[2]
                    if review_rating > opinion_border:
                        # positive word count
                        new_positive = tuple[1] + 1
                    if review_rating < opinion_border:
                        # negative word count
                        new_negative = tuple[2] + 1
                    dictionary[token] = (new_total, new_positive, new_negative)
                else:
                    if review_rating > opinion_border:
                        dictionary[token] = (1, 1, 0)
                    if review_rating < opinion_border:
                        dictionary[token] = (1, 0, 1)
    positive_list = []
    negative_list = []
    for word in dictionary:
        if '#' in word or word == '':
            continue
        positive_divident = get_prob(float(dictionary[word][1]), float(review_count))
        positive_divider = get_prob(float(dictionary[word][0]), float(review_count)) * get_prob(
            float(class_count['positive']), float(review_count))
        positive_pmi = 0
        if positive_divider != 0 and positive_divident != 0:
            positive_pmi = math.log(positive_divident / positive_divider)

        negative_divident = get_prob(float(dictionary[word][2]), float(review_count))
        negative_divider = get_prob(float(dictionary[word][0]), float(review_count)) * get_prob(
            float(class_count['negative']), float(review_count))
        negative_pmi = 0
        if negative_divider != 0 and negative_divident != 0:
            negative_pmi = math.log(negative_divident / negative_divider)

        semantic_orientation = positive_pmi - negative_pmi
        if semantic_orientation > 0:
            positive_list.append((word, semantic_orientation))
        if semantic_orientation < 0:
            negative_list.append((word, semantic_orientation))
    sorted_positive = sorted(positive_list, key=lambda tup: tup[1], reverse=True)
    sorted_negative = sorted(negative_list, key=lambda tup: tup[1])
    return sorted_negative, sorted_positive


def save_lexicon(input_base, input):
    sorted_negative, sorted_positive = build_lexicon_poles(input, input_base)

    print len(sorted_positive)
    print len(sorted_negative)

    with codecs.open(OUTPUT_BASE + FILE_SEPARATOR + 'positive.txt', 'w', encoding='utf-8') as out:
        out.write(unicode(len(sorted_positive)))
        out.write('\n')
        for tuple in sorted_positive:
            out.write(unicode(tuple[0]) + "," + unicode(tuple[1]))
            out.write('\n')

    with codecs.open(OUTPUT_BASE + FILE_SEPARATOR + 'negative.txt', 'w', encoding='utf-8') as out:
        out.write(unicode(len(sorted_negative)))
        out.write('\n')
        for tuple in sorted_negative:
            out.write(unicode(tuple[0]) + "," + unicode(tuple[1]))
            out.write('\n')


def get_prob(divident, divider):
    if divider == 0:
        return float(0)
    else:
        return divident / divider


if __name__ == '__main__':
    save_lexicon(INPUT_BASE, INPUT)
    # movies = get_movies_as_dict(INPUT_BASE, INPUT)

    # review = 0
    # for movie in movies:
    # review += len(movies[movie][1])
    #
    # print review