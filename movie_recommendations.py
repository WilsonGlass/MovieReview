"""
Name: movie_recommendations.py
Date: 1 April 2021
Author: Wilson Glass
Description: Movie Review Program
"""

import math
import csv
from scipy.stats import pearsonr
class BadInputError(Exception):
    pass

class Movie: 
    def __init__(self, id, title):

        """ 
        Constructor.
        Initializes the following instances variables.  You
        must use exactly the same names for your instance 
        variables.  (For testing purposes.)
        id: the id of the movie
        title: the title of the movie
        users: list of the id's of the users who have
            rated this movie.  Initially, this is
            an empty list, but will be filled in
            as the training ratings file is read.
        similarities: a dictionary where the key is the
            id of another movie, and the value is the similarity
            between the "self" movie and the movie with that id.
            This dictionary is initially empty.  It is filled
            in "on demand", as the file containing test ratings
            is read, and ratings predictions are made.
        """
        # INSTANCE VARIABLES #
        self.users = []
        self.id = id 
        self.title = title
        self.similarities = {}

    def __str__(self):
        """
        Returns string representation of the movie object.
        Handy for debugging.
        """
        return("id: " + str(self.id) + "title: " + str(self.title))



    def __repr__(self):
        """
        Returns string representation of the movie object.
        """
        return("id: " + str(self.id) + "title: " + self.title + "list of users: " + self.users + "similarity: " + self.similarities)



    def get_similarity(self, other_movie_id, movie_dict, user_dict):
        """ 
        Returns the similarity between the movie that 
        called the method (self), and another movie whose
        id is other_movie_id.  (Uses movie_dict and user_dict)
        If the similarity has already been computed, return it.
        If not, compute the similarity (using the compute_similarity
        method), and store it in both
        the "self" movie object, and the other_movie_id movie object.
        Then return that computed similarity.
        If other_movie_id is not valid, raise BadInputError exception.
        """
        # RAISES BADINPUT IF OTHERMOVIE IS NONE #
        if movie_dict.get(other_movie_id) == None:
            raise BadInputError
        elif self.similarities.get(other_movie_id) == None:
            # FINDS SIMILARITIES W/ MOVIE/USER DICT #
            value = self.compute_similarity(other_movie_id,movie_dict,user_dict)
            self.similarities.update({other_movie_id : value})
            movie_dict.get(other_movie_id).similarities.update({self.id : value})

        return self.similarities.get(other_movie_id)

        

    def compute_similarity(self, other_movie_id, movie_dict, user_dict):
        """ 
        Computes and returns the similarity between the movie that 
        called the method (self), and another movie whose
        id is other_movie_id.  (Uses movie_dict and user_dict)
        """
        diff = 0
        num_users = 0
        for user_id in user_dict:
            # FINDS SIMILARITIES / AVERAGE DIFF #
            if self.id in user_dict[user_id] and other_movie_id in user_dict[user_id]:
                diff += abs(float(user_dict[user_id][self.id]) - float(user_dict[user_id][other_movie_id]))
                num_users += 1

        if num_users == 0:
            return 0

        # CALCULATES AVERAGE, SIMILARITY, RETURNS #
        avg_diff = diff / num_users 
        similarity = float(1 - (avg_diff/4.5))
        return similarity



class Movie_Recommendations():
    # Constructor
    def __init__(self, movie_filename, training_ratings_filename):
        """
        Initializes the Movie_Recommendations object from 
        the files containing movie names and training ratings.  
        The following instance variables should be initialized:
        self.movie_dict - A dictionary that maps a movie id to
               a movie objects (objects the class Movie)
        self.user_dict - A dictionary that maps user id's to a 
               a dictionary that maps a movie id to the rating
               that the user gave to the movie.    
        """
        f = open(movie_filename, 'r', encoding = 'utf8')
        csv_reader = csv.reader(f, delimiter = ',', quotechar = '"')
        f.readline()
        self.movie_dict = {}

        for line in csv_reader:
            # store movie object with current line id and title into movie dicitonary at key of movie ID #
            # These will need to be changed to ints besides the movie title #
            id = int(line[0])
            title = line[1]
            self.movie_dict[id] = Movie(id, title)
        f.close()
        f = open(training_ratings_filename, 'r', encoding = 'utf8')
        csv_reader = csv.reader(f, delimiter = ',', quotechar = '"')
        f.readline()

        #make an accumulator dictionary. keep appending to it until you reach the next user - when new person is reached you append the accumulator
        # to the user dictionary #
        tempdict = {}
        actualdict = {}
        user = 1
        for line in csv_reader:
            if int(line[0]) == user:
                tempdict[int(line[1])] = float(line[2])
            else:
                actualdict[user] = tempdict
                tempdict = {}
                user += 1
                tempdict[int(line[1])] = float(line[2])
            self.movie_dict[int(line[1])].users.append(user)
        actualdict[user] = tempdict
        self.user_dict = actualdict


    def predict_rating(self, user_id, movie_id):
        """
        Returns the predicted rating that user_id will give to the
        movie whose id is movie_id. 
        If user_id has already rated movie_id, return
        that rating.
        If either user_id or movie_id is not in the database,
        then BadInputError is raised.
        """
        sum_of_products = 0
        sum_of_sim = 0
        # IF USER OR MOVIE NOT RECOGNIZED RAISES BADINPUT #
        if self.user_dict.get(user_id) == None or self.movie_dict.get(movie_id) == None:
            raise BadInputError
        elif self.user_dict.get(user_id).get(movie_id) != None:
            return self.user_dict.get(user_id).get(movie_id)

        for movie in self.user_dict.get(user_id):
            # RATING USED IN RECOMMENDATION #
            sum_of_products += self.movie_dict.get(movie).get_similarity(movie_id,
                self.movie_dict, self.user_dict) * self.user_dict.get(user_id).get(movie)
            sum_of_sim += self.movie_dict.get(movie).get_similarity(movie_id,
                self.movie_dict, self.user_dict)

        # IF ZERO, EQUALS 2.5 #
        if(sum_of_sim == 0):
            return 2.5 

        return round(sum_of_products/sum_of_sim,2)

    def predict_ratings(self, test_ratings_filename):
        """
        Returns a list of tuples, one tuple for each rating in the
        test ratings file.
        The tuple should contain
        (user id, movie title, predicted rating, actual rating)
        """
        print(test_ratings_filename)
        lists = []
        with open(test_ratings_filename, newline = "\n", encoding = 'utf8') as csvfile:
            lines = csv.reader(csvfile, delimiter = ',')
            count = 0
            for line in lines:
                # APPENDS VALUES TO TUPLE #
                if count == 0:  
                    count += 1
                    continue
                lists.append((int(line[0]), self.movie_dict.get(int(line[1])).title, 
                    self.predict_rating(int(line[0]), int(line[1])), float(line[2])))

        return lists


    def correlation(self, predicted_ratings, actual_ratings):
        """
        Returns the correlation between the values in the list predicted_ratings
        and the list actual_ratings.  The lengths of predicted_ratings and
        actual_ratings must be the same.
        """
        return pearsonr(predicted_ratings, actual_ratings)[0]

if __name__ == "__main__":
    # Create movie recommendations object.
    movie_recs = Movie_Recommendations("movies.csv", "training_ratings.csv")
    # Predict ratings for user/movie combinations
    rating_predictions = movie_recs.predict_ratings("test_ratings.csv")
    print("Rating predictions: ")
    for prediction in rating_predictions:
        print(prediction)
    predicted = [rating[2] for rating in rating_predictions]
    actual = [rating[3] for rating in rating_predictions]
    correlation = movie_recs.correlation(predicted, actual)
    print(f"Correlation: {correlation}")    