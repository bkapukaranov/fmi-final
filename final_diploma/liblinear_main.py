__author__ = 'inspir3d'

import math
import collections
import codecs
import review_util
from liblinearutil import *
from random import randint
import numpy as np
import ordinal_logistic

INPUT_BASE = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/data/raw_reviews'
INPUT = ['cinexio_movie_reviews_full_filtered.tsv']
OUTPUT_BASE = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/data'
OUTPUT_TRAIN = 'cinexio_train.txt'
OUTPUT_TEST = 'cinexio_test.txt'
EMO_NEG = 'neg_emoticons.lst'
EMO_POS = 'pos_emoticons.lst'
EMO_BASE = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/data'
LEXICON_IN_BASE = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/data'
LEXICON_POSITIVE = 'positive.txt'
LEXICON_NEGATIVE = 'negative.txt'
TSV_SEPARATOR = "\t"
FILE_SEPARATOR = "/"
NEGATIVE_BOUNDARY = 2.0
POSITIVE_BOUNDARY = 3.5


def add_vector_class(vector, review_rating):
    vector_class = 'b'
    if review_rating > POSITIVE_BOUNDARY:
        vector_class = 'a'
    if review_rating < NEGATIVE_BOUNDARY:
        vector_class = 'c'
    vector.append(vector_class)

def add_vector_regression_score(vector, review_rating):
        vector.append(review_rating)


def get_clean_tokens(review_text):
    tokens = review_text.replace(':)', '') \
        .replace('.', '') \
        .replace(',', '') \
        .replace('?', '') \
        .replace('!', '') \
        .replace('(', '') \
        .replace(')', '') \
        .replace(';', '') \
        .replace(':', '') \
        .replace('--', '-') \
        .replace('"', '') \
        .lower().split(" ")
    return tokens


def add_lexicon_scores(negative, positive, review_text, vector):
    tokens = get_clean_tokens(review_text)
    positive_score = 0.0
    negative_score = 0.0
    for token in tokens:
        if token in positive:
            positive_score += float(positive[token])
        if token in negative:
            negative_score += float(negative[token])

    vector.append(positive_score)
    vector.append(negative_score)


def write_vector(out, score, vector):
    out.write(str(score))
    for x in range(0, len(vector)):
        if vector[x] != 0.0:
            out.write(' ' + str(x+1) + ':' + str(vector[x]))
    out.write('\n')


def get_globals(movies):
    global_word_list = set()
    for movie_dict in movies:
        for review_dict in movie_dict['reviews']:
            review_text = review_dict['r_text']
            tokens = get_clean_tokens(review_text)
            for token in tokens:
                global_word_list.add(token)
    return global_word_list


def add_bag_of_words(global_word_list, review_text, vector):
    for token in global_word_list:
        if token in review_text.lower():
            vector.append(float(1))
        else:
            vector.append(float(0))


def get_emoticon_lists():
    pos_emoticons = set()
    with open(EMO_BASE + FILE_SEPARATOR + EMO_POS, 'r') as ff:
        for line in ff:
            pos_emoticons.add(line)

    neg_emoticons = set()
    with open(EMO_BASE + FILE_SEPARATOR + EMO_NEG, 'r') as ff:
        for line in ff:
            neg_emoticons.add(line)
    return neg_emoticons, pos_emoticons


def add_emoticon_features(neg_emoticons, pos_emoticons, review_text, vector):
    for emoticon in pos_emoticons:
        if unicode(emoticon.replace('\n',''), "ISO-8859-1") in review_text:
            vector.append(float(1))
        else:
            vector.append(float(0))
    for emoticon in neg_emoticons:
        if unicode(emoticon.replace('\n',''), "ISO-8859-1") in review_text:
            vector.append(float(1))
        else:
            vector.append(float(0))


def get_bigrams(movies):
    bigrams = set()
    for movie_dict in movies:
        for review_dict in movie_dict['reviews']:
            review_text = review_dict['r_text']
            tokens = get_clean_tokens(review_text)
            for x in range(0, len(tokens)-1, 2):
                bigrams.add((tokens[x], tokens[x+1]))
    return bigrams


def add_bigrams(global_bigrams, review_text, vector):
    for tuple in global_bigrams:
        if tuple[0] in review_text and tuple[1] in review_text:
            vector.append(float(1))
        else:
            vector.append(float(0))


def add_movie_len(len, vector):
    vector.append(float(len))


def add_movie_imdb_rating(imdb_rating, vector):
    if imdb_rating != 'null':
        vector.append(float(imdb_rating))
    else:
        vector.append(0.0)


def add_movie_cinexio_rating(cinexio_rating, vector):
    if cinexio_rating != 'null':
        vector.append(float(cinexio_rating))
    else:
        vector.append(0.0)


def get_directors(movies):
    directors = set()
    for movie in movies:
        director = movie['director']
        directors.add(director)
    return directors


def get_actors(movies):
    global_actors = set()
    for movie in movies:
        actors = movie['actors']
        for actor in actors:
            global_actors.add(actor)
    return global_actors


def get_countries(movies):
    global_countries = set()
    for movie in movies:
        country = movie['country']
        global_countries.add(country)
    return global_countries


def get_genres(movies):
    global_genres = set()
    for movie in movies:
        genres = movie['genres']
        for genre in genres:
            global_genres.add(genre)
    return global_genres


def get_user_average_rating(movies):
    global_user_stats = {}
    global_user_ave = {}
    for movie in movies:
        reviews = movie['reviews']
        for review in reviews:
            user = review['r_name']
            user_rating = review['r_rating']
            if user not in global_user_stats:
                global_user_stats[user] = [user_rating]
            else:
                global_user_stats[user].append(user_rating)
    for user in global_user_stats:
        sum = 0.0
        for rating in global_user_stats[user]:
            sum += float(rating)
        global_user_ave[user] = sum / len(global_user_stats[user])
    return global_user_ave


def add_director(global_directors, director, vector):
    for dir in global_directors:
        if dir == director:
            vector.append(float(1))
        else:
            vector.append(float(0))


def add_actors(global_actors, actors, vector):
    for actor in global_actors:
        if actor in actors:
            vector.append(float(1))
        else:
            vector.append(float(0))


def add_country(global_countries, country, vector):
    for g_country in global_countries:
        if g_country == country:
            vector.append(float(1))
        else:
            vector.append(float(0))


def add_genres(global_genres, genres, vector):
    for genre in global_genres:
        if genre in genres:
            vector.append(float(1))
        else:
            vector.append(float(0))


def add_user_ave(user_ave_rating, vector):
    vector.append(user_ave_rating)


def getX_Y(global_user_ave, global_word_list, movies, neg_emoticons, negative_lex, pos_emoticons, positive_lex):
    y = []
    x = []
    for movie_dict in movies:
        for review_dict in movie_dict['reviews']:
            review_text = review_dict['r_text']
            review_rating = float(review_dict['r_rating'])

            vector = []

            # text features
            add_vector_regression_score(y, review_rating) # 1
            add_lexicon_scores(negative_lex, positive_lex, review_text, vector) # 2
            add_bag_of_words(global_word_list, review_text, vector) # 8406
            add_emoticon_features(neg_emoticons, pos_emoticons, review_text, vector) # 123 + 77
            # add_bigrams(global_bigrams, review_text, vector)

            # context features
            add_movie_len(movie_dict['length'], vector) # 1
            add_movie_imdb_rating(movie_dict['imdb_rating'], vector) # 1
            add_movie_cinexio_rating(movie_dict['cinexio_rating'], vector) # 1
            add_director(global_user_ave, movie_dict['director'], vector)
            add_actors(global_user_ave, movie_dict['actors'], vector)
            add_country(global_user_ave, movie_dict['country'], vector)
            add_genres(global_user_ave, movie_dict['genres'], vector)
            # add_user_ave(global_user_ave[review_dict['r_name']], vector) # 1

            # add user average rating for genre
            # add user average rating for country

            with open(OUTPUT_BASE + FILE_SEPARATOR + OUTPUT_TRAIN, 'a') as out:
                write_vector(out, review_rating, vector)

            x.append(vector)
    return x, y


def run_liblinear(train_movies, test_movies, global_movies, negative_lex, positive_lex, params):

    global_word_list = get_globals(global_movies)
    neg_emoticons, pos_emoticons = get_emoticon_lists()
    global_bigrams = get_bigrams(global_movies)
    global_directors = get_directors(global_movies)
    global_actors = get_actors(global_movies)
    global_countries = get_countries(global_movies)
    global_genres = get_genres(global_movies)
    global_user_ave = get_user_average_rating(global_movies)

    trainx, trainy = getX_Y(global_countries, global_word_list, train_movies, neg_emoticons, negative_lex, pos_emoticons, positive_lex)
    testx, testy = getX_Y(global_countries, global_word_list, test_movies, neg_emoticons, negative_lex, pos_emoticons, positive_lex)
    print 'len train x: ' + str(len(trainx))
    print 'len test x: ' + str(len(testx))
    print '# features: ' + str(len(trainx[0]))
    print 'global_dict len ' + str(len(global_word_list))
    print 'global_bigrams len ' + str(len(global_bigrams))
    print 'global_directors len ' + str(len(global_directors))
    print 'global_actors len ' + str(len(global_actors))
    print 'global_countries len ' + str(len(global_countries))
    print 'global_genres len ' + str(len(global_genres))
    print 'global_user_ave len ' + str(len(global_user_ave))
    print 'emo pos len: ' + str(len(pos_emoticons))
    print 'emo neg len: ' + str(len(neg_emoticons))
    # print 'total set len ' + str(len(train_movies))
    #print 'final MSE: ' + str(MSE)

    model = train(trainy, trainx, params)
    p_labs, p_acc, p_vals = predict(testy, testx, model)

    ME = 0.0
    for index in range(0, len(p_labs)):
        ME += (testy[index] - p_labs[index]) * (testy[index] - p_labs[index])
    MSE = ME / len(p_labs)

    print testy
    print p_labs
    return MSE


def run_liblinear_kfold(movies, negative_lex, positive_lex, params):

    global_word_list = get_globals(movies)
    neg_emoticons, pos_emoticons = get_emoticon_lists()
    global_bigrams = get_bigrams(movies)
    global_directors = get_directors(movies)
    global_actors = get_actors(movies)
    global_countries = get_countries(movies)
    global_genres = get_genres(movies)
    global_user_ave = get_user_average_rating(movies)

    x, y = getX_Y(global_user_ave, global_word_list, movies, neg_emoticons, negative_lex, pos_emoticons, positive_lex)
    print 'len x: ' + str(len(x))
    print '# features: ' + str(len(x[0]))
    print 'global_dict len ' + str(len(global_word_list))
    print 'global_bigrams len ' + str(len(global_bigrams))
    print 'global_directors len ' + str(len(global_directors))
    print 'global_actors len ' + str(len(global_actors))
    print 'global_countries len ' + str(len(global_countries))
    print 'global_genres len ' + str(len(global_genres))
    print 'global_user_ave len ' + str(len(global_user_ave))
    print 'emo pos len: ' + str(len(pos_emoticons))
    print 'emo neg len: ' + str(len(neg_emoticons))
    print 'total set len ' + str(len(movies))
    #print 'final MSE: ' + str(MSE)

    MSE = train(y, x, params)

    print "linear MSE: " + str(MSE)


def run_ordinal(movies, negative_lex, positive_lex):
    from sklearn import cross_validation

    global_word_list = get_globals(movies)
    neg_emoticons, pos_emoticons = get_emoticon_lists()
    global_user_ave = get_user_average_rating(movies)

    Xa, ya = getX_Y(global_user_ave, global_word_list, movies, neg_emoticons, negative_lex, pos_emoticons, positive_lex)
    X = np.asarray(Xa)
    y = np.round(ya)
    y -= y.min()

    idx = np.argsort(y)
    X = X[idx]
    y = y[idx]
    cv = cross_validation.ShuffleSplit(y.size, n_iter=5, test_size=.1, random_state=0)
    score_ordinal_logistic = []
    for i, (train, test) in enumerate(cv):
        #test = train
        if not np.all(np.unique(y[train]) == np.unique(y)):
            # we need the train set to have all different classes
            continue
        assert np.all(np.unique(y[train]) == np.unique(y))
        train = np.sort(train)
        test = np.sort(test)
        w, theta = ordinal_logistic.ordinal_logistic_fit(X[train], y[train], verbose=True,
                                        solver='TNC')
        pred = ordinal_logistic.ordinal_logistic_predict(w, theta, X[test])
        s = ordinal_logistic.metrics.mean_squared_error(y[test], pred)
        print('ERROR (ORDINAL)  fold %s: %s' % (i+1, s))
        score_ordinal_logistic.append(s)

    print('MEAN SQUARED ERROR (ORDINAL LOGISTIC):    %s' % np.mean(score_ordinal_logistic))


def run_logistic_regression(movies, negative, positive):
    MSE = 0.0
    for index in range(0, 5):
        train_movies = []
        test_movies = []
        for movie in movies:
            if randint(0, 9) < 2:
                test_movies.append(movie)
            else:
                train_movies.append(movie)

        print 'train len - ' + str(len(train_movies))
        print 'test len - ' + str(len(test_movies))

        fold_mse = run_liblinear(train_movies, test_movies, movies, negative, positive, '-q')
        MSE += fold_mse
    print "logistic regression MSE: " + str(MSE / 5)


def build_liblinear_vectors(input_base, input):
    movies = review_util.movies_as_list(input_base, input)
    print "movies len: " + str(len(movies))

    ave_histogram_rating = dict()
    for movie in movies:
        imdb_rating = movie['imdb_rating']
        cinexio_rating = movie['cinexio_rating']
        if imdb_rating == 'null':
            imdb_rating = '0.0'
        if cinexio_rating == 'null':
            cinexio_rating = '0.0'

        if float(cinexio_rating) < 2.5:
            print movie['name']
        if cinexio_rating not in ave_histogram_rating:
            ave_histogram_rating[cinexio_rating] = (float(imdb_rating), 1)
        else:
            ave_histogram_rating[cinexio_rating] = (ave_histogram_rating[cinexio_rating][0] + float(imdb_rating), ave_histogram_rating[cinexio_rating][1] + 1)

    ordered = collections.OrderedDict(sorted(ave_histogram_rating.items()))
    for key in ordered:
        print "("+str(key) + "," + str(ordered[key][0]/ordered[key][1]) +")" + str(ordered[key][1])

    print 'done'

    ###
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

    print 'lexicon pos: ' + str(len(positive))
    print 'lexicon neg: ' + str(len(negative))

    # run_logistic_regression(movies, negative, positive)
    run_liblinear_kfold(movies, negative, positive, '-s 11 -v 5 -q')
    # run_ordinal(movies, negative, positive)
    ###

if __name__ == '__main__':
    build_liblinear_vectors(INPUT_BASE, INPUT)
