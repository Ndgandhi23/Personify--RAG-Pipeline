#Schemas for the user and application collections in the MongoDB database.
class User:
    def __init__(self, email, password):
        self.email = email
        self.password = password

    def to_dict(self):
        return {
            "email": self.email,
            "password": self.password
        }

class Application:
    def __init__(self, email, date, company, company_email, status):
        self.email = email
        self.date = date
        self.company = company
        self.company_email = company_email
        self.status = status

    def to_dict(self):
        return {
            "email": self.email,
            "date": self.date,
            "company": self.company,
            "company_email": self.company_email,
            "status": self.status
        }