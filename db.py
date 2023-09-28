import sqlite3
import security as s


def connectDb(name="database.db"):
    return sqlite3.connect(name, check_same_thread=False)


connection = connectDb("website.db")


# ---------------------------------
# users
def createUsersTable():
    cursor = connection.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    full_name TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
    cursor.execute(query)
    connection.commit()


def addUser(name, username, password):
    cursor = connection.cursor()
    query = """
    INSERT INTO users(full_name,username,password) VALUES (?,?,?)
    """
    cursor.execute(
        query,
        (
            name,
            username,
            password,
        ),
    )
    connection.commit()


def updateUserPassword(userid, password):
    cursor = connection.cursor()
    query = """
    UPDATE users
    SET password = ?
    WHERE userid = ?
    """
    cursor.execute(query, (password, userid))
    connection.commit()


def checkUsernameExists(username):
    cursor = connection.cursor()
    query = """
    SELECT id FROM users WHERE username = ?
    """
    cursor.execute(query, (username,))

    if cursor.fetchone():
        return True
    else:
        return False


def getUserId(username):
    cursor = connection.cursor()
    query = """
    SELECT id FROM users WHERE username = ?
    """
    cursor.execute(query, (username,))

    return cursor.fetchone()[0]


def loginUserDb(username, password):
    cursor = connection.cursor()
    query = """
    SELECT password FROM users WHERE username = ?
    """
    cursor.execute(query, (username,))
    stored_hashpassword = cursor.fetchone()
    return s.checkPassMatch(stored_hashpassword, password)


def getInfoUsers(user_id):
    cursor = connection.cursor()
    query = """
    SELECT * FROM users WHERE id = ?
    """
    cursor.execute(query, (user_id,))
    return cursor.fetchone()


def getInfoAllComments():
    cursor = connection.cursor()
    query = """
    SELECT * FROM users 
    """
    cursor.execute(
        query,
    )
    return cursor.fetchall()


# -----------------------------------------
# Movie Uploader


def createUploadersTable():
    cursor = connection.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS uploaders(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
    )
    """
    cursor.execute(query)
    connection.commit()


def addUploader(name, email, password):
    cursor = connection.cursor()
    query = """
    INSERT INTO uploaders(full_name,email,password) VALUES (?,?,?)
    """
    cursor.execute(
        query,
        (
            name,
            email,
            password,
        ),
    )
    connection.commit()


def checkEmailExists(email):
    cursor = connection.cursor()
    query = """
    SELECT id FROM uploaders WHERE email = ?
    """
    cursor.execute(query, (email,))

    if cursor.fetchone():
        return True
    else:
        return False


def getUploaderId(email):
    cursor = connection.cursor()
    query = """
    SELECT id FROM uploaders WHERE email = ?
    """
    cursor.execute(query, (email,))
    return cursor.fetchone()[0]


def loginUploaderDb(email, password):
    cursor = connection.cursor()
    query = """
    SELECT password FROM uploaders WHERE email = ?
    """
    cursor.execute(query, (email,))
    stored_hashpassword = cursor.fetchone()
    return s.checkPassMatch(stored_hashpassword, password)


def getInfoUploader(uploader_id):
    cursor = connection.cursor()
    query = """
    SELECT * FROM uploaders WHERE id = ?
    """
    cursor.execute(query, (uploader_id,))
    return cursor.fetchone()


# --------------------------
# MOVIES TABLE


def createMoviesTable():
    cursor = connection.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS movies(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    uploader_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    rate INTEGER NOT NULL,
    image_url TEXT NOT NULL,
    video_url TEXT NOT NULL,
    FOREIGN KEY (uploader_id) REFERENCES uploaders (id) 
    )
    """
    cursor.execute(query)
    connection.commit()


def addMovie(
    uploader_id,
    movie_name,
    movie_description,
    rate,
    movie_image_path,
    movie_video_path,
):
    cursor = connection.cursor()
    query = """
    INSERT INTO movies(uploader_id,name,description,rate,image_url,video_url) VALUES (?,?,?,?,?,?)
    """
    cursor.execute(
        query,
        (
            uploader_id,
            movie_name,
            movie_description,
            rate,
            movie_image_path,
            movie_video_path,
        ),
    )
    connection.commit()


def getAllMovies():
    cursor = connection.cursor()
    query = """SELECT * FROM movies"""
    cursor.execute(query)
    return cursor.fetchall()


def getMovie(movie_id):
    cursor = connection.cursor()
    query = """ 
    SELECT * FROM movies WHERE id = ?
    """
    cursor.execute(query, (movie_id,))
    return cursor.fetchone()


def getUploaderOfMovie(movie_id):
    cursor = connection.cursor()
    query = """
    SELECT uploader_id FROM movies WHERE id = ?
    """
    cursor.execute(query, (movie_id,))
    return cursor.fetchone()[0]


def get_user(username):
    cursor = connection.cursor()
    query = """SELECT * FROM users WHERE username = ?"""
    cursor.execute(query, (username,))
    return cursor.fetchone()


def checkMovieNameFound(movie_name):
    cursor = connection.cursor()
    query = """
    SELECT id from movies WHERE name like ? OR description LIKE ?
    """
    movie_name = f"%{movie_name}%"
    cursor.execute(
        query,
        (
            movie_name,
            movie_name,
        ),
    )
    movie_id = cursor.fetchone()
    if movie_id:
        return movie_id[0]
    else:
        return False


def checkSameImage(filename):
    cursor = connection.cursor()
    query = """
    SELECT image_url from movies 
    """
    cursor.execute(query)
    all_image_urls = cursor.fetchall()
    pathoffilename = f"/static/uploads_posters/{filename}"
    for image in all_image_urls:
        if image[0] == pathoffilename:
            return True

    return False


def checkSameVideo(filename):
    cursor = connection.cursor()
    query = """
    SELECT video_url from movies 
    """
    cursor.execute(query)
    all_videos_urls = cursor.fetchall()
    pathoffilename = f"/static/uploads_videos/{filename}"
    for video in all_videos_urls:
        if video[0] == pathoffilename:
            return True

    return False


def createDownloadedTable():
    cursor = connection.cursor()
    query = """
    CREATE TABLE IF NOT EXISTS downloaded(
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    movie_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (movie_id) REFERENCES movies (id),
    FOREIGN KEY (user_id) REFERENCES users (id)
    )
    """
    cursor.execute(query)
    connection.commit()


def addaDownloaded(movie_id, user_id):
    cursor = connection.cursor()
    query = """
    INSERT INTO users(movie_id,user_id) VALUES (?,?)
    """
    cursor.execute(
        query,
        (
            movie_id,
            user_id,
        ),
    )
    connection.commit()


def getmoviesforUsers(user_id):
    cursor = connection.cursor()
    query = """
    SELECT * 
    FROM movies m JOIN downloaded d
    ON  m.id = d.movie_id
    WHERE d.user_id = ?
    """
    cursor.execute(query, (user_id,))
    return cursor.fetchall()


def getmoviesNumber():
    cursor = connection.cursor()
    query = """
    SELECT count(*) 
    FROM movies m JOIN downloaded d
    ON  m.id = d.movie_id
    """
    cursor.execute(query, ())
    return cursor.fetchall()


# -----------------------------------------
# Comment Section


def createCommentsTable():
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            movie_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (movie_id) REFERENCES movies (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    """
    )

    connection.commit()


def add_comment(movie_id, user_id, text):
    cursor = connection.cursor()
    query = """INSERT INTO comments (movie_id, user_id, text) VALUES (?, ?, ?)"""
    cursor.execute(query, (movie_id, user_id, text))
    connection.commit()


def get_comments_for_movie(movie_id):
    cursor = connection.cursor()
    query = """
        SELECT  users.username, comments.text, comments.timestamp
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.movie_id = ?
    """
    cursor.execute(query, (movie_id,))
    return cursor.fetchall()


def getAllComments():
    cursor = connection.cursor()
    query = """
    SELECT * 
    FROM comments
    """
    cursor.execute(
        query,
    )
    return cursor.fetchone()


def getcommentsNumber():
    cursor = connection.cursor()
    query = """
        SELECT  count(*)
        FROM comments
        JOIN users ON comments.user_id = users.id
    """
    cursor.execute(query, ())
    return cursor.fetchall()
