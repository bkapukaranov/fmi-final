__author__ = 'Borislav Kapukaranov'

import codecs
import os

OUTPUT_TSV = "/Users/inspir3d/FMI/MasterDiploma/fmi-final/cinexio_movie_reviews_28_04.tsv"
CINEXIO_RAW_MOVIE_DATA_PATH = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/cinexio_raw_movie_data_28_04'
SEPARATOR = "\t"


def movie_ratings_workarounds(response):
    overall_rating = '0.0'
    imdb_rating = 'null'
    imdb_url = 'null'
    # workarounds to find the cinexio rating
    if response.body.find("IMDB") != -1 and response.body.find("METACRITIC") == -1 and response.body.find("ROTTEN TOMATOES") == -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[1][:-2]
        imdb_rating = response.xpath("//span[@class='rating']/text()").extract()[0]
        imdb_url = response.xpath("//span[@class='rated-by']/a/@href").extract()[0]
    if response.body.find("IMDB") != -1 and response.body.find("METACRITIC") != -1 and response.body.find("ROTTEN TOMATOES") == -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[2][:-2]
        imdb_rating = response.xpath("//span[@class='rating']/text()").extract()[0]
        imdb_url = response.xpath("//span[@class='rated-by']/a/@href").extract()[0]
    if response.body.find("IMDB") != -1 and response.body.find("METACRITIC") == -1 and response.body.find("ROTTEN TOMATOES") != -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[2][:-2]
        imdb_rating = response.xpath("//span[@class='rating']/text()").extract()[0]
        imdb_url = response.xpath("//span[@class='rated-by']/a/@href").extract()[0]
    if response.body.find("IMDB") != -1 and response.body.find("METACRITIC") != -1 and response.body.find("ROTTEN TOMATOES") != -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[3][:-2]
        imdb_rating = response.xpath("//span[@class='rating']/text()").extract()[0]
        imdb_url = response.xpath("//span[@class='rated-by']/a/@href").extract()[0]
    if response.body.find("IMDB") != -1 and response.body.find("METACRITIC") != -1 and response.body.find("ROTTEN TOMATOES") != -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[3][:-2]
    if response.body.find("IMDB") == -1 and response.body.find("METACRITIC") != -1 and response.body.find("ROTTEN TOMATOES") != -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[2][:-2]
    if response.body.find("IMDB") != -1 and response.body.find("METACRITIC") == -1 and response.body.find("ROTTEN TOMATOES") != -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[2][:-2]
    if response.body.find("IMDB") != -1 and response.body.find("METACRITIC") != -1 and response.body.find("ROTTEN TOMATOES") == -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[2][:-2]
    if response.body.find("IMDB") == -1 and response.body.find("METACRITIC") == -1 and response.body.find("ROTTEN TOMATOES") != -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[1][:-2]
    if response.body.find("IMDB") != -1 and response.body.find("METACRITIC") == -1 and response.body.find("ROTTEN TOMATOES") == -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[1][:-2]
    if response.body.find("IMDB") == -1 and response.body.find("METACRITIC") != -1 and response.body.find("ROTTEN TOMATOES") == -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[1][:-2]
    if response.body.find("IMDB") == -1 and response.body.find("METACRITIC") == -1 and response.body.find("ROTTEN TOMATOES") == -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[0][:-2]
    #   end of workaround to find the cinexio rating
    return imdb_rating, imdb_url, overall_rating


def parse_review(response):
    if not os.path.exists(CINEXIO_RAW_MOVIE_DATA_PATH):
        os.makedirs(CINEXIO_RAW_MOVIE_DATA_PATH)

    body = response.body
    cinexio_index = response.url[response.url.rfind('/')+1:]

    with open(CINEXIO_RAW_MOVIE_DATA_PATH + '/' + cinexio_index + ".html", 'w') as f:
        f.write(body)

    movie_url = response.url
    movie_name = response.xpath("//div[@class='title']/text()").extract()[0].replace('\n', '').strip()
    director = response.xpath("//div[@class='detail director']/span[@class='value']/text()").extract()[0].replace('\n', '').strip()
    stars = response.xpath("//div[@class='detail stars']/span[@class='value']/text()").extract()[0].replace('\n', '').strip()
    country = response.xpath("//div[@class='detail country']/span[@class='value']/text()").extract()[0].replace('\n', '').strip()
    genre = response.xpath("//div[@class='detail genre']/span[@class='value']/text()").extract()[0].replace('\n', '').strip()
    runtime = response.xpath("//div[@class='detail runtime']/span[@class='value']/text()").extract()[0].replace('\n', '').strip()

    imdb_rating, imdb_url, overall_rating = movie_ratings_workarounds(response)

    ratings = response.xpath("//ul/li[@class='review']/div[@class='rating']")
    reviews = response.xpath("//ul/li[@class='review']/div[@class='text']/text()").extract()
    users = response.xpath("//ul/li[@class='review']/div[@class='name']/text()").extract()
    dates = response.xpath("//ul/li[@class='review']/div[@class='date']/text()").extract()
    len_ratings = len(ratings)
    len_reviews = len(reviews)
    len_users = len(users)
    len_dates = len(dates)
    if len_ratings != len_reviews and len_ratings != len_users and len_ratings != len_dates:
        print "ratings, reviews and users are with different lengths: ratings:" + str(len_ratings) + " vs reviews:" + \
              str(len_reviews) + " vs users:" + str(len_users) + " vs dates:" + str(len_dates)
        return -1

    # write data to csv
    with codecs.open(OUTPUT_TSV, "a", encoding="utf-8") as f:
        print "====== " + movie_name + " ======"

        f.write(movie_name + SEPARATOR + overall_rating + SEPARATOR + movie_url + SEPARATOR + imdb_url + SEPARATOR + imdb_rating
                + SEPARATOR + director + SEPARATOR + stars + SEPARATOR + country + SEPARATOR + genre + SEPARATOR + runtime)
        f.write('\n')
        f.write(str(len_reviews))
        f.write('\n')

        for index in range(len_reviews):
            this_rating = ratings[index]
            this_review = reviews[index]
            this_user = users[index]
            this_date = dates[index]

            fullstars = len(this_rating.xpath(".//i[@class='star fa fa-star']").extract())
            halfstars = len(this_rating.xpath(".//i[@class='star fa fa-star-half-o']").extract())
            nostars = len(this_rating.xpath(".//i[@class='star fa fa-star-o']").extract())
            processed_rating = fullstars + halfstars * 0.5
            print "rating:"
            print "full " + str(fullstars)
            print "half " + str(halfstars)
            print "no " + str(nostars)
            print "combined " + str(processed_rating)

            processed_review = this_review.replace('\n', '').strip()
            print "review: " + processed_review

            print "user: " + this_user

            print "date: " + this_date

            f.write(this_user + SEPARATOR + processed_review + SEPARATOR + str(processed_rating) + SEPARATOR + str(this_date))
            f.write('\n')

    return None