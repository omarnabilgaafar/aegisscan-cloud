class User:
    def __init__(self, user_id=None, username="", email="", password_hash="", created_at=None):
        self.id = user_id
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.created_at = created_at