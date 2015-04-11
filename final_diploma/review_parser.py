__author__ = 'Borislav Kapukaranov'

import codecs
import os

OUTPUT_TSV = "/Users/inspir3d/FMI/MasterDiploma/fmi-final/cinexio_movie_reviews_11_04.tsv"
CINEXIO_RAW_MOVIE_DATA_PATH = '/Users/inspir3d/FMI/MasterDiploma/fmi-final/cinexio_raw_movie_data_11_04'
SEPARATOR = "\t"

def parse_review(response):
    if not os.path.exists(CINEXIO_RAW_MOVIE_DATA_PATH):
        os.makedirs(CINEXIO_RAW_MOVIE_DATA_PATH)

    body = response.body
    cinexio_index = response.url[response.url.rfind('/')+1:]

    with open(CINEXIO_RAW_MOVIE_DATA_PATH + '/' + cinexio_index + ".html", 'w') as f:
        f.write(body)

    movie_name = response.xpath("//div[@class='title']/text()").extract()[0].replace('\n', '').strip()
    movie_url = response.url
    overall_rating = '0.0'
    imdb_rating = 'null'
    imdb_url = 'null'

    if response.body.find("IMDB") != -1 and response.body.find("METACRITIC") == -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[1][:-2]
        imdb_rating = response.xpath("//span[@class='rating']/text()").extract()[0]
        imdb_url = response.xpath("//span[@class='rated-by']/a/@href").extract()[0]

    if response.body.find("IMDB") != -1 and response.body.find("METACRITIC") != -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[2][:-2]
        imdb_rating = response.xpath("//span[@class='rating']/text()").extract()[0]
        imdb_url = response.xpath("//span[@class='rated-by']/a/@href").extract()[0]

    if response.body.find("IMDB") == -1 and response.body.find("METACRITIC") != -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[1][:-2]

    if response.body.find("IMDB") == -1 and response.body.find("METACRITIC") == -1:
        overall_rating = response.xpath("//span[@class='rating']/text()").extract()[0][:-2]

    ratings = response.xpath("//ul/li[@class='review']/div[@class='rating']")
    reviews = response.xpath("//ul/li[@class='review']/div[@class='text']/text()").extract()
    len_ratings = len(ratings)
    len_reviews = len(reviews)
    if len_ratings != len_reviews:
        print "ratings and reviews are with different lengths: " + str(len_ratings) + " vs " + str(len_reviews)
        return -1

    # write data to csv
    with codecs.open(OUTPUT_TSV, "a", encoding="utf-8") as f:
        print "====== " + movie_name + " ======"

        f.write(movie_name + SEPARATOR + overall_rating + SEPARATOR + movie_url + SEPARATOR + imdb_url + SEPARATOR + imdb_rating)
        f.write('\n')
        f.write(str(len_reviews))
        f.write('\n')

        for index in range(len_reviews):
            this_rating = ratings[index]
            this_review = reviews[index]

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

            f.write(processed_review + SEPARATOR + str(processed_rating))
            f.write('\n')

    return None