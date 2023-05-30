import json
import datetime
import random
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS, cross_origin
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import requests
from sqlalchemy import Integer, func, or_
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///library.sqlite3"
app.config["SECRET_KEY"] = "random string"
CORS(app)

db = SQLAlchemy(app)


# Books model
class Books(db.Model):
    id = db.Column("ID", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    author = db.Column(db.String(100))
    year_published = db.Column(db.String(100))
    book_type = db.Column(db.Integer)

    def __init__(self, name, author, year_published, book_type):
        self.name = name
        self.author = author
        self.year_published = year_published
        self.book_type = book_type

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "author": self.author,
            "year_published": self.year_published,
            "book_type": self.book_type,
        }


# Function to fetch bookS data from open libary API and add it to the database,
# we only call this function once to fill the database with an actual data.
# sources:
#   Open Libary:https://openlibrary.org/subjects/python.json
#               https://openlibrary.org/subjects/cooking.json
#               https://openlibrary.org/subjects/humor.json
#               https://openlibrary.org/subjects/kids_books.json
#               https://openlibrary.org/subjects/exercise.json


# def fetch_and_add_books():
#     url = "https://openlibrary.org/subjects/exercise.json"
#     response = requests.get(url)
#     data = response.json()

#     for work in data.get("works", []):
#         book_data = work.get("title", "")
#         author_data = work.get("authors", [])
#         year_published = work.get("first_publish_year", "")

#         if isinstance(book_data, dict):
#             book_name = book_data.get("title", "")
#         else:
#             book_name = book_data

#         # Check if a book with the same name already exists
#         existing_book = Books.query.filter_by(name=book_name).first()
#         if existing_book:
#             continue  # Ignore the book if it already exists in the database

#         # Extract the book name, author, and year published from the data
#         authors = [author.get("name", "") for author in author_data]
#         if isinstance(year_published, int):
#             year_published = datetime.datetime(year_published, 1, 1).year
#         else:
#             year_published = None

#         book_type = random.randint(1, 3)

#         new_book = Books(
#             book_name, ", ".join(authors), year_published, book_type
#         )
#         db.session.add(new_book)

#     db.session.commit()


# Function to display books
@app.route("/show-books", methods=["GET"])
def show_books():
    books_list = [book.to_dict() for book in Books.query.all()]
    return jsonify(books_list)


@app.route("/search-books/<search_query>", methods=["GET"])
def search_books(search_query):
    # Perform the search based on the provided search_query
    search_results = Books.query.filter(Books.name.ilike(f"%{search_query}%")).all()

    # Serialize the search results into a list of dictionaries
    serialized_results = []
    for book in search_results:
        serialized_book = {
            "name": book.name,
            "author": book.author,
            "year_published": book.year_published,
            "book_type": book.book_type,
            "id": book.id,
        }
        serialized_results.append(serialized_book)

    # Return the search results as JSON
    return jsonify(serialized_results)


# Function to add a book


@app.route("/add-book", methods=["POST"])
def add_book():
    data = request.get_json()
    name = data.get("name")
    author = data.get("author")
    year_published = data.get("year_published")
    book_type = data.get("book_type")

    # Check if a book with the same name already exists
    existing_book = Books.query.filter_by(name=name).first()
    if existing_book:
        return "A book with the same name already exists."

    # Find duplicate book names
    duplicate_books = (
        db.session.query(Books.name, db.func.count(Books.name))
        .group_by(Books.name)
        .having(db.func.count(Books.name) > 1)
        .all()
    )

    # Iterate over duplicate book names and remove duplicates
    for book_name, count in duplicate_books:
        duplicate_entries = Books.query.filter_by(name=book_name).all()
        for duplicate_entry in duplicate_entries[1:]:
            db.session.delete(duplicate_entry)
            db.session.commit()

    new_book = Books(name, author, year_published, book_type)
    db.session.add(new_book)
    db.session.commit()
    return "A new record was created."


# Function to delete a book
@app.route("/delete-book/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    book = Books.query.get(book_id)
    if book:
        db.session.delete(book)
        db.session.commit()
        return "Book deleted."
    else:
        return "Book not found."


# Get a single book info
@app.route("/get-book/<book_id>", methods=["GET"])
def get_book(book_id):
    book = Books.query.get(book_id)
    return jsonify(book.to_dict())


# Function to update a book
@app.route("/update-book/<book_id>", methods=["PUT"])
def update_book(book_id):
    data = request.get_json()
    name = data.get("name")
    author = data.get("author")
    year_published = data.get("year_published")
    type_book = data.get("type_book")

    book = Books.query.get(book_id)
    if book:
        book.name = name
        book.author = author
        book.year_published = year_published
        book.type_book = type_book
        db.session.commit()
        return "The record was updated."
    else:
        return "Book not found."
    # Function to search books by name


@app.route("/search-books-name")
def searchBooksName():
    search_term = request.args.get("search", "")
    books_list = [
        book.to_dict()
        for book in Books.query.filter(
            or_(
                func.lower(Books.name).like(f"%{search_term}%"),
                func.lower(Books.author).like(f"%{search_term}%"),
            )
        )
    ]
    json_data = json.dumps(books_list)
    return json_data


# End of function
# Function to search books by ID


@app.route("/search-books-id")
def searchBooksID():
    search_term = int(request.args.get("search", ""))
    books_list = [
        book.to_dict()
        for book in Books.query.filter(
            or_(func.cast(Books.id, Integer).like(f"%{search_term}%"))
        )
    ]
    json_data = json.dumps(books_list)
    return json_data


# End of function


# Customers model
class Customers(db.Model):
    id = db.Column("ID", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    city = db.Column(db.String(100))
    age = db.Column(db.String(100))

    def __init__(self, name, city, age):
        self.name = name
        self.city = city
        self.age = age

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "city": self.city,
            "age": self.age,
        }


# Function to display customers
@app.route("/show-customers", methods=["GET"])
def show_customers():
    customers_list = [customer.to_dict() for customer in Customers.query.all()]
    return jsonify(customers_list)


# Function to add a customer
@app.route("/add-customer", methods=["POST"])
def add_customer():
    data = request.get_json()
    name = data.get("name")
    city = data.get("city")
    age = data.get("age")

    new_customer = Customers(name, city, age)
    db.session.add(new_customer)
    db.session.commit()
    return "A new record was created."


# Function to delete a customer
@app.route("/delete-customer/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    customer = Customers.query.get(customer_id)
    if customer:
        db.session.delete(customer)
        db.session.commit()
        return "Customer deleted."
    else:
        return "Customer not found."


# Get a single customer info
@app.route("/get-customer/<customer_id>", methods=["GET"])
def get_customer(customer_id):
    customer = Customers.query.get(customer_id)
    return jsonify(customer.to_dict())


# Function to search customers by name


@app.route("/search-customer-name")
def searchCustomerName():
    search_term = request.args.get("search", "").lower()
    customers_list = [
        customer.to_dict()
        for customer in Customers.query.filter(
            or_(func.lower(Customers.name).like(f"%{search_term}%"))
        )
    ]
    json_Data = json.dumps(customers_list)
    return json_Data


# End of function searching customers


# Function to search books by ID
@app.route("/search-customer-id")
def searchCustomersID():
    search_term = int(request.args.get("search", ""))
    books_list = [
        book.to_dict()
        for book in Customers.query.filter(
            or_(func.cast(Customers.id, Integer).like(f"%{search_term}%"))
        )
    ]
    json_data = json.dumps(books_list)
    return json_data


# Function to update a customer
@app.route("/update-customer/<customer_id>", methods=["PUT"])
def update_customer(customer_id):
    data = request.get_json()
    name = data.get("name")
    city = data.get("city")
    age = data.get("age")

    customer = Customers.query.get(customer_id)
    if customer:
        customer.name = name
        customer.city = city
        customer.age = age
        db.session.commit()
        return "The record was updated."
    else:
        return "Customer not found."


class Loans(db.Model):
    id = db.Column("ID", db.Integer, primary_key=True)
    custid = db.Column("custid", db.Integer, db.ForeignKey("customers.ID"))
    bookid = db.Column("bookid", db.Integer, db.ForeignKey("books.ID"))
    loandate = db.Column(db.Date)
    returndate = db.Column(db.Date)
    status = db.Column(db.String)

    customer = relationship("Customers", foreign_keys=[custid])
    book = relationship("Books", foreign_keys=[bookid])

    def __init__(self, custid, bookid, loandate, returndate, status):
        self.custid = custid
        self.bookid = bookid
        self.loandate = loandate
        self.returndate = returndate
        self.status = status

    def to_dict(self):
        return {
            "id": self.id,
            "custid": self.custid,
            "bookid": self.bookid,
            "loandate": self.loandate,
            "returndate": self.returndate,
            "status": self.status,
            "customer_name": self.customer.name,
            "book_name": self.book.name,
        }


# Function to display loans


@app.route("/show-loans", methods=["GET"])
def show_loans():
    loans_list = [loan.to_dict() for loan in Loans.query.all()]
    return jsonify(loans_list)


# Function to add a loan
@app.route("/add-loan", methods=["POST"])
def add_loan():
    try:
        data = request.get_json()
        cust_id = int(data["cust_id"])
        book_id = int(data["book_id"])
        loan_date = datetime.strptime(data["loan_date"], "%d/%m/%Y").date()
        return_date = datetime.strptime(data["return_date"], "%d/%m/%Y").date()
        status = data["status"]

        # Check if a loan with the same cust_id and book_id already exists
        existing_loan = Loans.query.filter_by(custid=cust_id, bookid=book_id).first()
        if existing_loan:
            return "Loan already exists for the given customer and book."
        customer = Customers.query.get(cust_id)
        book = Books.query.get(book_id)

        if not customer or not book:
            return "Invalid customer or book."

        # Calculate the loan duration based on book_type
        book_type_to_days = {
            1: timedelta(days=10),
            2: timedelta(days=5),
            3: timedelta(days=2),
        }
        loan_duration = book_type_to_days.get(book.book_type)
        if loan_duration:
            return_date = loan_date + loan_duration
            return_date_formatted = return_date.strftime(
                "%d/%m/%Y"
            )  # Format the date as dd/mm/yyyy

            new_loan = Loans(
                custid=cust_id,
                bookid=book_id,
                loandate=loan_date,
                returndate=return_date,
                status=status,
            )
            db.session.add(new_loan)
            db.session.commit()

            # Return the formatted date in the response
            return jsonify(
                message="A new loan was created.", return_date=return_date_formatted
            )
        else:
            return "Invalid book type."
    except Exception as error:
        print("error: %s" % error)


# Function to delete a loan
@app.route("/delete-loan/<int:loan_id>", methods=["DELETE"])
def delete_loan(loan_id):
    loan = Loans.query.get(loan_id)
    if loan:
        db.session.delete(loan)
        db.session.commit()
        return "Loan deleted."
    else:
        return "Loan not found."


# Function to get a specific loan
@app.route("/get-loan/<int:loan_id>", methods=["GET"])
def get_loan(loan_id):
    loan = Loans.query.get(loan_id)
    if loan:
        loan_dict = loan.to_dict()
        loan_dict["loandate"] = loan_dict["loandate"].strftime("%Y-%m-%d")
        loan_dict["returndate"] = loan_dict["returndate"].strftime("%Y-%m-%d")
        return jsonify(loan_dict)
    else:
        return "Loan not found."


# Function for updating loan
@app.route("/update-loan", methods=["POST", "PUT"])
@app.route("/update-loan/<id>", methods=["POST", "PUT"])
def update_loan(id=-1):
    try:
        data = request.get_json()
        loan_id = int(data["loan_id"])
        loan_date = datetime.strptime(data["loan_date"], "%Y-%m-%d").date()

        existing_loan = Loans.query.get(loan_id)
        if not existing_loan:
            return "Loan not found."

        # Calculate the return date based on the book's loan duration
        loan_duration = get_loan_duration(existing_loan.book)
        return_date = loan_date + timedelta(days=loan_duration)

        existing_loan.loandate = loan_date
        existing_loan.returndate = return_date
        db.session.commit()

        return "Loan updated successfully."
    except Exception as error:
        print("Error: %s" % error)
        return "An error occurred while updating the loan"


def get_loan_duration(book):
    # Define loan duration based on book type
    book_type_to_days = {
        1: 10,
        2: 5,
        3: 2,
    }
    return book_type_to_days.get(book.book_type, 0)


# Function to get expired loans
@app.route("/expired-loans", methods=["GET"])
def expired_loans():
    today = datetime.utcnow().date()
    expired_loans = Loans.query.filter(Loans.returndate < today).all()
    return render_template("expired_loans.html", loans=expired_loans)


# Function for returning a loan
@app.route("/return-loan/<int:loan_id>", methods=["PUT"])
def return_loan(loan_id):
    try:
        loan = Loans.query.get(loan_id)
        if not loan:
            return "Loan not found."

        loan.status = "return"  # Update the loan status to "deactive"
        db.session.commit()

        return "Loan returned successfully."
    except Exception as error:
        print("Error: %s" % error)
        return "An error occurred while returning the loan."


if __name__ == "__main__":
    with app.app_context():
        # fetch_and_add_books()
        db.create_all()
    app.run(debug=True)
