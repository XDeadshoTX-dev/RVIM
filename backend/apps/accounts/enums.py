class HttpStatus:
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    CONFLICT = 409
    UNPROCESSABLE_ENTITY = 422
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500


class ResponseMessage:
    USER_CREATED = "User successfully created"
    USER_LOGGED_IN = "User successfully logged in"
    USER_LOGGED_OUT = "User successfully logged out"
    INVALID_CREDENTIALS = "Invalid email or password"
    EMAIL_ALREADY_EXISTS = "Email already registered"
    VALIDATION_ERROR = "Validation error"
    UNAUTHORIZED = "Unauthorized access"
    FORBIDDEN = "Access forbidden"
    RATE_LIMIT_EXCEEDED = "Too many requests. Please try again later"
    INVALID_REQUEST = "Invalid request data"