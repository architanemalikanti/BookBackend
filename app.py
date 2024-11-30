import json

from flask import Flask
from flask import jsonify
from flask import request

app = Flask(__name__)





#Brandon - route 1: return a list of books that a user owns. 

#Archita - route 2: return ALL the books available on this app!

#Archita - route 3: return ALL the users using this app!

#Archita - route 4: display the user's picture, username, First/Last Name, liked/bookmarked books

#Brandon - route 5: return all the kinds of genres available (return the genre table entries)

#Archita - route 6: return a book's properties (id, title, image, author, description, etc)

#Brandon- route 7: return all the books for a specific genre (ex: "scifi" returns all books in scifi)

#future: how to create a user profile? picture, books to add (web scraping), edit profile










#route number 1
@app.route("/post", methods = ['POST'])

def create_post():
    


#route number 2: 
@app.route("/api/posts/", methods = ['GET'])
def get_posts():
    print("Hello World")




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)
