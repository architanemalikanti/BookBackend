import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)










#future: how to create a user profile? picture, books to add (web scraping), edit profile






    


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

#Archita: route number 2: return ALL the books available on this app!
@app.route("/books/", methods=["GET"])
def get_all_books():
    """
    Return all books available on this app
    """
    books = Book.query.all()
    return jsonify({"all_books": [book.serialize() for book in books]}), 200


#Archita - route 3: return ALL the users using this app!
@app.route("/users/", methods=["GET"])
def get_all_users():
    """
    Return all the users using this app
    """
    users = User.query.all()
    return jsonify({"all_users": [user.serialize() for user in users]}), 200


#Archita - route 4: display the user's picture, username, First/Last Name, liked/bookmarked books
@app.route("/user/<int:user_id>/profile/", methods=["GET"])
def get_user_profile(user_id):
    """
    Display the user's picture, username, location, and liked/bookmarked books
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.serialize()), 200


#Brandon - route 5: return all the kinds of genres available (return the genre table entries)
@app.route("/genres/")
def get_all_genres():
    """
    Return all genres
    """
    genres = Genre.query.all()
    return json.dumps("genres": genre.simple_serialize()), 200

#Archita - route 6: return a book's properties (id, title, image, author, description, etc)
@app.route("/book/<int:book_id>/", methods=["GET"])
def get_book_details(book_id):
    """
    Return a book's properties (id, title, image, author, description, etc)
    """
    book = Book.query.filter_by(id=book_id).first()
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.serialize()), 200

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
