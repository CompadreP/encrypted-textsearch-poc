class BaseMySQLError(Exception):
    pass


class MySQLPoolIsNotInitializedError(BaseMySQLError):
    pass


class MySQLPoolIsAlreadyInitializedError(BaseMySQLError):
    pass
