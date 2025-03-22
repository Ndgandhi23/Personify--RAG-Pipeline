#Schemas for the user and application collections in the MongoDB database.
# schema.py
class User:
    def __init__(self, email, password, searches=None):
        self.email = email
        self.password = password
        self.searches = searches if searches is not None else []

    def add_search(self, search_query):
        # Add new search to the beginning of the list
        self.searches.insert(0, search_query)
        # Keep only the 5 most recent searches
        self.searches = self.searches[:5]

    def to_dict(self):
        return {
            "email": self.email,
            "password": self.password,
            "searches": self.searches
        }