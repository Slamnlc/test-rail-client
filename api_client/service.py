class Auth:
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def __call__(self, r):
        r.auth = (self.username, self.password)
        return r

    def __del__(self):
        return 'BasicAuth'
