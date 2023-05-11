class ExpiresTimes:
    ACCESS_EXPIRES = None
    REFRESH_EXPIRES = None


def set_expires_time(access_time, refresh_time):
    ExpiresTimes.ACCESS_EXPIRES = access_time
    ExpiresTimes.REFRESH_EXPIRES = refresh_time