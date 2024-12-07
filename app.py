import json
from flask import Flask, jsonify, request
from db import db, User, Book, Genre
import datetime
import users_dao  


app = Flask(__name__)
db_filename = "/usr/app/book.db"

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

# Initialize the database
db.init_app(app)

# Base route
@app.route("/")
def base_route():
    return json.dumps("Welcome to the ultimate book sharing app!"), 200

# Route 8: User Likes a Book, and then Checks if a Matching Happens with the person who posted the book (kinda like a tinder match). 
@app.route("/books/like_and_match", methods=["POST"])
def Like_And_Matching():
    body = json.loads(request.data)

    #we get the user that sends the like (their username, string)

    liker_username = body.get("userA")

    #we get the ID of the person who posted the book (their username, string)
    book_id = body.get("userB")

    #double check:
    if liker_username == None or book_id == None:
        return json.dumps({"error": "Problem with loading User Data."}), 400

    #check if this username is in the Book Owner's liked books array. 

    #step 1: get the book, given the book owner's ID. 
    book = Book.query.filter_by(id=book_id).first()
    if not book:
        return jsonify({"error": "Book not found"}), 404
    
    #step 2: get owner of the book:
    book_owner = book.posted_by_user
    if not book_owner:
        return jsonify({"error": "Book owner not found"}), 404
    
    #step 3: get liker. 
    liker = User.query.filter_by(username=liker_username).first()
    if not liker:
        return jsonify({"error": "Liker user not found"}), 404


    for book in book_owner.bookmarked_books:
        if book.posted_by_user == liker:  # Check if user is equal to liker
        # Match is found, add eachother as friends and return this to frontend. 
            liker.add_friend(book_owner)
            book_owner.add_friend(liker)
            return jsonify({
                "match": True,
                "message": f"{liker_username} and {book_owner.username} have matched!",
                "users": {
                    "liker": liker.simple_serialize(),
                    "owner": book_owner.simple_serialize(),
                },
                "books": {
                    "liker_book": book.posted_by_user.simple_serialize(),
                    "owner_book": book.name
                }
            }), 200
    
    #if the user is not in this dictionary, then just return None. 
    return json.dumps({"match": False, "message": "No match found."}), 200


# Route 9: Return a User's friends. 
@app.route("/user/<int:user_id>/friends/", methods=["GET"])
def get_user_friends(user_id):
    user = User.query.get(user_id)
    if user is None:
        return json.dumps({"error": "User not found."}), 404
    
    return json.dumps({"friends": [friend.simple_serialize() for friend in user.friends]}), 200
    



# generalized response formats
def success_response(data, code=200):
    """
    Generalized success response function
    """
    return json.dumps(data), code

def failure_response(message, code=404):
    """
    Generalized failure response function
    """
    return json.dumps({"error": message}), code


def extract_token(request):
    """
    Helper function that extracts the token from the header of a request
    """
    auth_header = request.header.get("Authorization")
    if auth_header is None:
        return False, json.dumps({"error": "missing auth header."})
    bearer_token = auth_header.replace("Bearer", "").strip()
    if not bearer_token:
        return False, json.dumps({"error": "invalid auth header"})
    return True, bearer_token


@app.route("/register/", methods=["POST"])
def register_account():
    """
    Endpoint for registering a new user
    """
    body = json.loads(request.data)
    email = body.get("email")
    password = body.get("password")

    if email is None or password is None:
        return json.dumps({"error": "Invalid email or password."})
    
    created, user = users_dao.create_user(email, password)

    if not created:
        return json.dumps({"error": "User already exists."})
    
    return json.dumps({

        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "update_token": user.update_token,

    })
    pass


@app.route("/login/", methods=["POST"])
def login():
    """
    Endpoint for logging in a user
    """
    body = json.loads(request.data)
    email = body.get("email")
    password = body.get("password")

    if email is None or password is None:
        return json.dumps({"error": "Invalid Email or Password."}), 400
    
    success, user = users_dao.verify_credentials(email, password)

    if not success:
        return json.dumps({"error": "Incorrect Email/Password."}), 400
    
    return json.dumps(
        {
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "update_token": user.update_token,
        }
    )
    



@app.route("/session/", methods=["POST"])
def update_session():
    """
    Endpoint for updating a user's session
    """
    success, update_token = extract_token(request)
    if not success:
        return update_token
    
    user = users_dao.renew_session(update_token)

    if user is None:
        return json.dumps({"error": "invalid update token."})
    
    return json.dumps(
        {
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "update_token": user.update_token,
        }
    )
    




@app.route("/secret/", methods=["GET"])
def secret_message():
    """
    Endpoint for verifying a session token and returning a secret message

    In your project, you will use the same logic for any endpoint that needs 
    authentication
    """
    success, session_token = extract_token(request)
    if not success: 
        return session_token
    
    user = users_dao.get_user_by_session_token(session_token)

    if user is None or not user.verify_session_token(session_token):
        return json.dumps({"error": "Invalid session token."})
    
    return json.dumps({"message": "Implemented Session Token."}), 200





@app.route("/logout/", methods=["POST"])
def logout():
    """
    Endpoint for logging out a user
    """
    success, session_token = extract_token(request)
    if not success:
        return session_token
    
    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return json.dumps({"error": "Invalid Session Token."}), 400
    user.session_expiration = datetime.datetime.now()
    db.session.commit()
    return json.dumps({"message": "User has successfully logged out."})


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

#Route 13: Delete user
@app.route("/user/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return json.dumps({"error": "User not found."}), 404
   
    db.session.delete(user)
    db.session.commit()
    return json.dumps(user.serialize()), 200

#Route 14: Delete book
@app.route("/book/<int:book_id>/", methods=["DELETE"])
def delete_book(book_id):
    book = Book.query.filter_by(id=book_id).first()
    if book is None:
        return json.dumps({"error": "Book not found."}), 404
   
    db.session.delete(book)
    db.session.commit()
    return json.dumps(book.serialize()), 200

#Route 15: Delete genre
@app.route("/genre/<string:genre_name>/", methods=["DELETE"])
def delete_genre(genre_name):
    genre = Genre.query.filter_by(genre=genre_name).first()
    if genre is None:
        return json.dumps({"error": "Genre not found."}), 404
   
    db.session.delete(genre)
    db.session.commit()
    return json.dumps(genre.serialize()), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(host="0.0.0.0", port=8000, debug=True)
