import json
from flask import Flask, jsonify, request
from db import db, User, Book, Genre

app = Flask(__name__)

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///books.db"  # Update with your database URI
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize the database
db.init_app(app)


# Route 1: Return a list of books that a user owns
@app.route("/user/<int:user_id>/books/")
def get_user_books(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify({"posted_books": [book.simple_serialize() for book in user.posted_books]}), 200


# Route 2: Return all books available on this app
@app.route("/books/", methods=["GET"])
def get_all_books():
    books = Book.query.all()
    return jsonify({"all_books": [book.serialize() for book in books]}), 200


# Route 3: Return all the users using this app
@app.route("/users/", methods=["GET"])
def get_all_users():
    users = User.query.all()
    return jsonify({"all_users": [user.serialize() for user in users]}), 200


# Route 4: Display the user's profile (picture, username, etc.)
@app.route("/user/<int:user_id>/profile/", methods=["GET"])
def get_user_profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.serialize()), 200


# Route 5: Return all the kinds of genres available
@app.route("/genres/", methods=["GET"])
def get_all_genres():
    genres = Genre.query.all()
    return jsonify({"genres": [genre.simple_serialize() for genre in genres]}), 200


# Route 6: Return a book's properties (id, title, image, author, description, etc.)
@app.route("/book/<int:book_id>/", methods=["GET"])
def get_book_details(book_id):
    book = Book.query.filter_by(id=book_id).first()
    if book is None:
        return jsonify({"error": "Book not found"}), 404
    return jsonify(book.serialize()), 200


# Route 7: Return all the books for a specific genre
@app.route("/genre/<string:genre_name>/books/", methods=["GET"])
def get_books_by_genre(genre_name):
    genre = Genre.query.filter_by(genre=genre_name).first()
    if genre is None:
        return jsonify({"error": "Genre not found"}), 404
    return jsonify({"genre_books": [book.simple_serialize() for book in genre.books]}), 200


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(host="0.0.0.0", port=8000, debug=True)
