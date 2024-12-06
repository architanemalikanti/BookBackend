import json
from flask import Flask, request
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
        return json.dumps({"error": "User not found"}), 404
    return json.dumps({"posted_books": [book.simple_serialize() for book in user.posted_books]}), 200


# Route 2: Return all books available on this app
@app.route("/books/", methods=["GET"])
def get_all_books():
    books = Book.query.all()
    return json.dumps({"all_books": [book.serialize() for book in books]}), 200


# Route 3: Return all the users using this app
@app.route("/users/", methods=["GET"])
def get_all_users():
    users = User.query.all()
    return json.dumps({"all_users": [user.serialize() for user in users]}), 200

# Route 4: Display the user's profile (picture, username, etc.)
@app.route("/user/<int:user_id>/profile/", methods=["GET"])
def get_user_profile(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dumps({"error": "User not found"}), 404
    return json.dumps(user.serialize()), 200


# Route 5: Return all the kinds of genres available
@app.route("/genres/", methods=["GET"])
def get_all_genres():
    genres = Genre.query.all()
    return json.dumps({"genres": [genre.simple_serialize() for genre in genres]}), 200


# Route 6: Return a book's properties (id, title, image, author, description, etc.)
@app.route("/book/<int:book_id>/", methods=["GET"])
def get_book_details(book_id):
    book = Book.query.filter_by(id=book_id).first()
    if book is None:
        return json.dumps({"error": "Book not found"}), 404
    return json.dumps(book.serialize()), 200


# Route 7: Return all the books for a specific genre
@app.route("/genre/<string:genre_name>/books/", methods=["GET"])
def get_books_by_genre(genre_name):
    genre = Genre.query.filter_by(genre=genre_name).first()
    if genre is None:
        return json.dumps({"error": "Genre not found"}), 404
    return json.dumps({"genre_books": [book.simple_serialize() for book in genre.books]}), 200

# Route 8: Create a new user
@app.route("/user/", methods=["POST"])
def create_user():
    body = json.loads(request.data)
    username = body.get("username")
    password = body.get("password")
    profile_photo = body.get("profile_photo")
    location = body.get("location")

    if not username or not password:
        return json.dumps({"error": "Username and password are required"}), 400

    # Check if the user already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return json.dumps({"error": "User with this username already exists"}), 409

    # Create a new user
    new_user = User(
        username=username, 
        password=password,
        profile_photo = profile_photo,
        location = location
    )
    
    db.session.add(new_user)
    db.session.commit()

    return json.dumps(new_user.serialize()), 201

# Route 9: Create a new book
@app.route("/book/<int:user_id>/", methods=["POST"])
def create_book(user_id):
    body = json.loads(request.data)
    name = body.get("name")
    description = body.get("description")
    genre_name = body.get("genre")
    genre = Genre.query.filter_by(genre=genre_name).first()
    photos = body.get("photos")
    user = User.query.filter_by(id=user_id).first()

    if user is None:
        return json.dumps({"error": "User not found"}), 404
    if genre is None:
        return json.dumps({"error": "Genre not found"}), 404

    new_book = Book(
        name=name, 
        description=description, 
        genre=genre, 
        photos=photos, 
        posted_by_user=user
    )
    db.session.add(new_book)
    user.posted_books.append(new_book)
    genre.books.append(new_book)
    db.session.commit()

    return json.dumps(new_book.serialize()), 201

# Route 10: Edit an existing book
@app.route("/book/<int:book_id>/edit/", methods=["POST"])
def edit_book(book_id):
    body = json.loads(request.data)
    name = body.get("name")
    description = body.get("description")
    genre_name = body.get("genre")
    genre = Genre.query.filter_by(genre=genre_name).first()
    photos = body.get("photos")

    book = Book.query.filter_by(id=book_id).first()
    if book is None:
        return json.dumps({"error": "Book not found"}), 404

    if name is not None: book.name = name
    if description is not None: book.description = description
    if genre is not None: book.genre = genre
    if photos is not None: book.photos = photos

    db.session.commit()

    return json.dumps(book.serialize()), 200

# Route 11: Like (bookmark) a book
@app.route("/book/<int:user_id>/<int:book_id>/like/", methods=["POST"])
def like_book(user_id, book_id):
    user = User.query.filter_by(id=user_id).first()
    book = Book.query.filter_by(id=book_id).first()

    if user is None:
        return json.dumps({"error": "User not found"}), 404
    if book is None:
        return json.dumps({"error": "Book not found"}), 404

    if book in user.bookmarked_books:
        return json.dumps({"message": "Book already liked"}), 200

    user.bookmarked_books.append(book)
    book.bookmarked_by_users.append(user)
    db.session.commit()

    return json.dumps({"message": "Book liked successfully"}), 200

# Route 12: Create genre
@app.route("/genre/", methods=["POST"])
def create_genre():
    body = json.loads(request.data)
    genre = body.get("genre")

    if genre is None:
        return json.dumps({"error": "Genre is empty."}), 400

    new_genre = Genre(
        genre = genre
    )

    db.session.add(new_genre)
    db.session.commit()

    return json.dumps(new_genre.serialize()), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(host="0.0.0.0", port=8000, debug=True)
