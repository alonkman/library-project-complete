from app import get_book, run


def get_book_test():
    print(get_book(12))

if __name__ == '__main__':
    run()
    print("testing:\n")
    get_book_test()


#     class Loan(db.Model):
#     _tablename_ = 'loans'
#     cust_id = Column(Integer, ForeignKey('customers.id'), primary_key=True)
#     book_id = Column(Integer, ForeignKey('books.id'), primary_key=True)
#     loan_date = Column(Date)
#     return_date = Column(Date)

#     customer = relationship("Customer", backref="loans")
#     book = relationship("Book", backref="loans")

#     def _repr_(self):
#         return f"<Loan(cust_id={self.cust_id}, book_id={self.book_id}, loan_date='{self.loan_date}', return_date='{self.return_date}')>"

#     def to_dict(self):
#         return {
#             'cust_id': self.cust_id,
#             'book_id': self.book_id,
#             'loan_date': self.loan_date,
#             'return_date': self.return_date,
#         }


# @app.route("/all_loan")
# def loan_show():
#     loans_list = [loan.to_dict() for loan in Loan.query.all()]
#     json_data = json.dumps(loans_list, cls=CustomJSONEncoder)
#     return json_data


# @app.route('/bookloan', methods=['POST'])
# def bookloan():
#     data = request.get_json()
#     cust_id = int(data['cust_id'])
#     book_id = int(data['book_id'])
#     loan_date = datetime.strptime(data['loan_date'], '%d/%m/%Y').date()
#     return_date = datetime.strptime(data['return_date'], '%d/%m/%Y').date()

#     # Check if a loan with the same cust_id and book_id already exists
#     existing_loan = Loan.query.filter_by(
#         cust_id=cust_id, book_id=book_id).first()
#     if existing_loan:
#         return "Loan already exists for the given customer and book."

#     new_loan = Loan(cust_id=cust_id, book_id=book_id,
#                     loan_date=loan_date, return_date=return_date)
#     db.session.add(new_loan)
#     db.session.commit()
#     return "A new record was created."