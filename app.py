import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)






#Archita - route 2: return ALL the books available on this app!

#Archita - route 3: return ALL the users using this app!

#Archita - route 4: display the user's picture, username, First/Last Name, liked/bookmarked books


#Archita - route 6: return a book's properties (id, title, image, author, description, etc)


#future: how to create a user profile? picture, books to add (web scraping), edit profile










#route number 1
@app.route("/post", methods = ['POST'])

def create_post():
    


#route number 2: 
@app.route("/api/posts/", methods = ['GET'])
def get_posts():
    print("Hello World")

#Brandon - route 1: return a list of books that a user owns. 
@app.route("/user/<int:user_id>/books/")
def get_user_books(user_id):
    """
    Return a list of books a user owns
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dumps({"error": "User not found"}), 404
    return json.dumps({"posted_books": [book.simple_serialize() for book in user.posted_books]}), 200

#Brandon - route 5: return all the kinds of genres available (return the genre table entries)
@app.route("/genres/")
def get_all_genres():
    """
    Return all genres
    """
    genres = Genre.query.all()
    return json.dumps("genres": genre.simple_serialize()), 200

#Brandon- route 7: return all the books for a specific genre (ex: "scifi" returns all books in scifi)
@app.route("/genre/<string:genre_name>/books/")
def get_books_by_genre(genre_name):
    """
    Return all books for a specific genre
    """
    genre = Genre.query.filter_by(genre=genre_name).first()
    if genre is None:
        return json.dumps({"error": "Genre not found."}), 404
    return json.dumps("genre_books": genre.serialize()), 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
