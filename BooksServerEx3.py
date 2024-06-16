import numpy
from flask import Flask, request, jsonify

app = Flask(__name__)


class Book:

    def __init__(self, title, author, year, price, genres):
        self.title = title
        self.author = author
        self.year = year
        self.price = price
        self.genres = genres
        self.id = 0

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "price": self.price,
            "year": self.year,
            "genres": self.genres
        }


AvailableId = 1
BooksList = list()


@app.route('/books/health', methods=['GET'])
def Health():
    return "OK", 200


@app.route('/book', methods=['POST'])
def CreateBook():
    global AvailableId
    title = request.json.get('title')
    year = request.json.get('year')
    price = request.json.get('price')
    found = False
    if year < 1940 or year > 2100:
        answer = {
            'errorMessage': f"Error: Can't create new Book that its year {year} is not in the accepted range [1940 -> 2100]"}
        return answer, 409
    if price <= 0:
        answer = {'errorMessage': "Error: Can't create new Book with negative price"}
        return answer, 409
    for book in BooksList:
        book.title.lower()
        if book.title == title:
            answer = {'errorMessage': f'Error: Book with the title {title} already exists in the system'}
            return answer, 409

    if not found:
        newBook = Book(title=title,
                       author=request.json.get('author').lower().title(),
                       year=year,
                       price=price,
                       genres=request.json.get('genres'))
        BooksList.append(newBook)
        newBook.id = AvailableId
        AvailableId += 1
        return jsonify({'result': newBook.id}), 200


@app.route('/books/total')
def total():
    args = request.args.to_dict()
    resBooks = FilterBooks(args, set(BooksList.copy()))
    genres = args.get('genres')
    if genres is not None:
        genres = genres.split(',')
        if not all(genre.isupper() for genre in genres):
            return jsonify({'error': 'Wrong case for genres'}), 400
    return jsonify({'result': len(resBooks)}), 200


def FilterBooks(args: dict, resBooks: set) -> set:
    RemovalSet = set()
    if args.get('author') is not None:
        for book in resBooks:
            if book.author != args.get('author').lower().title():
                RemovalSet.add(book)
    if args.get('price-bigger-than') is not None:
        for book in resBooks:
            if book.price < int(args.get('price-bigger-than')):
                RemovalSet.add(book)
    if args.get('price-less-than') is not None:
        for book in resBooks:
            if book.price > int(args.get('price-less-than')):
                RemovalSet.add(book)
    if args.get('year-bigger-than') is not None:
        for book in resBooks:
            if book.year < int(args.get('year-bigger-than')):
                RemovalSet.add(book)
    if args.get('year-less-than') is not None:
        for book in resBooks:
            if book.year > int(args.get('year-less-than')):
                RemovalSet.add(book)
    if args.get('genres') is not None:
        for book in resBooks:
            if not any(item in args.get('genres').split(',') for item in book.genres):
                RemovalSet.add(book)

    for item in RemovalSet:
        resBooks.discard(item)
    return resBooks


@app.route('/books')
def GetBooksData():
    args = request.args.to_dict()
    genres = args.get('genres')
    if genres is not None:
        genres = genres.split(',')
        if not all(genre.isupper() for genre in genres):
            return jsonify({'error': 'Wrong case for genres'}), 400
    resBooks = FilterBooks(args, set(BooksList.copy()))
    jsonBooksArr = [book.to_dict() for book in resBooks]
    jsonBooksArr = sorted(jsonBooksArr, key=lambda x: x['title'])

    return {'result': jsonBooksArr}, 200


@app.route('/book')
def GetSingleBookData():
    BookID = int(request.args.get('id'))
    for book in BooksList:
        if book.id == BookID:
            bookJson = book.to_dict()
            return {'result': bookJson}, 200

    return jsonify({'errorMessage': f'Error: no such Book with id {BookID}'}), 404


@app.route('/book', methods=['PUT'])
def UpdateBookPrice():
    bookID = request.args.get('id')
    try:
        bookID = int(bookID)
        bookItem = BooksList[bookID]
        if int(request.args.get('price')) <= 0:
            return jsonify({'errorMessage': f"Error: price update for book {bookID} must be a positive integer"}), 409
        oldPrice = bookItem.price
        bookItem.price = int(request.args.get('price'))
        return jsonify({'result': oldPrice}), 200
    except IndexError:
        return jsonify({'errorMessage': f"Error: no such Book with id {bookID}"}), 404


@app.route('/book', methods=['DELETE'])
def DeleteBook():
    bookID = int(request.args.get('id'))
    for book in BooksList:
        if book.id == bookID:
            BooksList.remove(book)
            return jsonify({'result': len(BooksList)}), 200
    return jsonify({'errorMessage': f"Error: no such Book with id {bookID}"}), 404


if __name__ == '__main__':
    app.run(debug=True,port=8574)
