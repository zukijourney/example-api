class InsufficientCreditsError(Exception):
    def __init__(self, available_credits: int, required_tokens: int):
        self.status_code = 429
        self.message = f'You have {available_credits} credits left. This request requires {required_tokens} credits.'
        super().__init__(self.message)

class NoProviderAvailableError(Exception):
    def __init__(self):
        self.status_code = 503
        self.message = 'No provider available.'
        super().__init__(self.message)

class AuthenticationError(Exception):
    def __init__(self, message: str, status_code: int = 401):
        self.status_code = status_code
        self.message = message
        super().__init__(self.message)

class AccessError(Exception):
    def __init__(self, message: str):
        self.status_code = 403
        self.message = message
        super().__init__(self.message)

class ValidationError(Exception):
    def __init__(self, message: str):
        self.status_code = 400
        self.message = message
        super().__init__(self.message)