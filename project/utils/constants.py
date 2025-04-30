class ErrorMessages:
    INVALID_CREDENTIALS = 'Could not validate credentials'
    WRONG_EMAIL_OR_PASSWORD = 'Wrong email or password'
    FORBIDDEN = 'Not enough permissions'

    EMAIL_EXISTS = 'Email already exists'
    USER_NOT_FOUND = 'User not found'
    USER_ALREADY_DELETED = 'User already deleted'
    USER_NOT_DELETED = 'User is not deleted'

    FRAMEWORK_NOT_FOUND = 'Framework not found'
    FRAMEWORK_EMPTY_ENTRIES = 'Framework must have at least one entry'
    FRAMEWORK_INVALID_KEYS = (
        "The following keys do not follow 'line X' pattern: {keys}"  # noqa
    )
    FRAMEWORK_NON_SEQUENTIAL = (
        'Line numbers in dict keys are not sequencial and/or not ordered'  # noqa
    )

    NOT_FOUND = 'Not found'
    LOGOUT_SUCCESS = 'Successfully logged out'
    USER_DELETED = 'User deleted'
