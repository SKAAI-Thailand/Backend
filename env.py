class DB:
    Host = "" # Your Database Host
    HostPort = 0 # Your Database Port
    Username = "" # Your Database Username
    Password = "" # Your Database User Password
    Database = "" # Your Database Name

class GOOGLE:
    CLIENT_ID = "" # Your Google OAuth CLIENT_ID
    CLIENT_SECRET = "" # Your Google OAuth CLIENT_SECRET
    REDIRECT_URI = [
        "{Your Frontend Domain}/google-oauth",
        "{Your Frontend Domain}/pwa/google-oauth"
    ]

class ROLE:
    unknown = "unknown"
    general = "general"
    admin = "admin"

class APPLICATION:
    version = "1.0"