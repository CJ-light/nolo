from flask import Flask, request, jsonify
from handlers.s3_handler import AWSBucketAPI
import handlers.dynamodb_handler as dynamodb
from handlers.pdf_handler import NoloPDFHandler

app = Flask(__name__)
bucket = AWSBucketAPI()
pdfhandler = NoloPDFHandler()
userpath = "img/"


@app.route("/")
def root_route():
    dynamodb.CreateTable()
    return "Resource Created"


#  Add a book entry
#  Route: http://localhost:5000/book
#  Method : POST
@app.route("/book", methods=["POST"])
def addABook():
    data = request.get_json()
    # id, title, author = 1001, 'Angels and Demons', 'Dan Brown'

    response = dynamodb.addItemToBook(data["id"], data["title"], data["author"])

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return {
            "msg": "Added successfully",
        }

    return {"msg": "Some error occcured", "response": response}


#  Read a book entry
#  Route: http://localhost:5000/book/<id>
#  Method : GET
@app.route("/book/<int:id>", methods=["GET"])
def getBook(id):
    response = dynamodb.GetItemFromBook(id)

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        if "Item" in response:
            return {"Item": response["Item"]}

        return {"msg": "Item not found!"}

    return {"msg": "Some error occured", "response": response}


#  Delete a book entry
#  Route: http://localhost:5000/book/<id>
#  Method : DELETE
@app.route("/book/<int:id>", methods=["DELETE"])
def DeleteABook(id):
    response = dynamodb.DeleteAnItemFromBook(id)

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return {
            "msg": "Deleted successfully",
        }

    return {"msg": "Some error occcured", "response": response}


#  Update a book entry
#  Route: http://localhost:5000/book/<id>
#  Method : PUT
@app.route("/book/<int:id>", methods=["PUT"])
def UpdateABook(id):
    data = request.get_json()

    # data = {
    #     'title': 'Angels And Demons',
    #     'author': 'Daniel Brown'
    # }

    response = dynamodb.UpdateItemInBook(id, data)

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return {
            "msg": "Updated successfully",
            "ModifiedAttributes": response["Attributes"],
            "response": response["ResponseMetadata"],
        }

    return {"msg": "Some error occured", "response": response}


#  Like a book
#  Route: http://localhost:5000/like/book/<id>
#  Method : POST
@app.route("/like/book/<int:id>", methods=["POST"])
def LikeBook(id):
    response = dynamodb.LikeABook(id)

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return {
            "msg": "Likes the book successfully",
            "Likes": response["Attributes"]["likes"],
            "response": response["ResponseMetadata"],
        }

    return {"msg": "Some error occured", "response": response}


# S3 Signed URL
@app.route("/get-images")
def get_images():
    # !IMPORTANT! : User access must be checked before get operation!
    # Users must only access their folders.
    return jsonify(bucket.get_files(userpath))


# PDF ETL Management
#  Convert PDF to Images
#  Route: http://localhost:5000/etl/imgconv
#  Method : GET
@app.route("/etl/imgconv")
def extract_images():
    try:
        response = pdfhandler.create_image_from_file()
        return jsonify({"msg": "File Converted", "hash_name": response}), 201
    except:
        return jsonify(response), 400


#  Convert Extract Text from PDF to Images
#  Route: http://localhost:5000/etl/txtconv
#  Method : GET
@app.route("/etl/txtconv")
def extract_text():
    try:
        response = pdfhandler.extract_text_from_file()
        return jsonify({"msg": "File Converted", "hash_name": response}), 201
    except:
        return jsonify(response), 400


if __name__ == "__main__":
    app.run(host="localhost", port=5000, debug=True)
