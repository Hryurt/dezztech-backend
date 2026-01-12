from datetime import timedelta

from src.config import settings

# JWT Configuration (imported from global settings)
# Note: SECRET_KEY and ALGORITHM are in global config (src.config.settings)
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES

# Token expiration timedelta
ACCESS_TOKEN_EXPIRE = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

# Password hashing configuration
PWD_SCHEMES = ["bcrypt"]
PWD_DEPRECATED = "auto"
