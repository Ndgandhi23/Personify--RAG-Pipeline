#Schemas for the user and application collections in the MongoDB database.
# schema.py
# schema.py
class User:
    def __init__(self, email, password, searches=None):
        self.email = email
        self.password = password
        self.searches = searches if searches is not None else []

    def to_dict(self):
        return {
            "email": self.email,
            "password": self.password,
            "searches": self.searches
        }

class Application:
    def __init__(self, user_email, date, company, company_email, role, status):
        self.user_email = user_email  # Linked to the email of the logged-in user
        self.date = date              # Date the application was created or updated
        self.company = company        # Company the application is being submitted to
        self.company_email = company_email  # The email of the company sending the notification
        self.role = role              # The role for which the application is being submitted
        self.status = status          # The current status of the application (e.g., Pending, Accepted)

    def to_dict(self):
        return {
            "user_email": self.user_email,
            "date": self.date,
            "company": self.company,
            "company_email": self.company_email,
            "role": self.role,
            "status": self.status
        }

#Question Schema
class Question:
    def __init__(self, question, answer=None):
        self.question = question  # The question text
        self.answer = answer      # The answer to the question (optional)

    def to_dict(self):
        return {
            "question": self.question,
            "answer": self.answer
        }