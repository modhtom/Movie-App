from db import *
from validators import *
from security import *
from flask import (
    Flask,
    request,
    redirect,
    render_template,
    flash,
    url_for,
    session,
    send_file,
)
import sqlite3
import hashlib
import bcrypt
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os


app = Flask(__name__)
app.secret_key = SECRET_KEY
limiter = Limiter(
    app=app, key_func=get_remote_address, default_limits=["50 per minute"]
)


@app.route("/", methods=["GET"])
def root_dir():
    return redirect("/home")


@app.route("/home", methods=["GET", "POST"])
def home():
    if session:
        if session["is_uploader"] == True:
            return render_template(
                "home_uploader.html",
                uploader=getInfoUploader(getUploaderId(session["email"])),
                movies=getAllMovies(),
                moviesnumber=getmoviesNumber(),
                commentnumber=getcommentsNumber(),
            )

        elif session["is_user"] == True:
            return render_template("view_movies.html", movies=getAllMovies())

    flash("Forbidden,You dont have access to this page , Please log in", "danger")
    return redirect("/login")


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def loginUser():
    if request.method == "GET":
        return render_template("signin.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if loginUserDb(username, password):
            session["logged_in"] = True
            session["is_user"] = True
            session["is_uploader"] = False
            session["username"] = username
            return redirect("/home")
        else:
            flash("Wrong username of password", "danger")
            return render_template("signin.html")


@app.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def registerUser():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        full_name = request.form["name"]
        username = request.form["username"]
        password = request.form["password"]
        if checkUsernameExists(username):
            flash("There is an account by this user", "danger")
            return render_template("register.html")
        if not (
            check_password_length(password) and check_password_characters(password)
        ):
            flash(
                "Invalid Password, Password should contain digits , lowercase character , upercase characters ,special characters",
                "danger",
            )
            return render_template("signup.html")

        hashed_password = hashPassword(password)
        addUser(full_name, username, hashed_password)
        return redirect("/login")


@app.route("/search", methods=["POST"])
def seachByName():
    movie_name = request.form["search_input"]
    movieid = checkMovieNameFound(movie_name)
    if movieid:
        return redirect(url_for("view_movie", movie_id=movieid))
    else:
        flash("Sorry We dont have this movie", "danger")
        return redirect(url_for("home"))


@app.route("/add-comment/<movie_id>", methods=["GET", "POST"])
def addComment(movie_id):
    if request.method == "POST":
        text = request.form["comment"]
        user_id = getUserId(session["username"])
        add_comment(movie_id, user_id, text)
        comments = get_comments_for_movie(movie_id)
        movie_info = getMovie(movie_id)
        return redirect(
            url_for(
                "view_movie",
                show_hidden_button=True,
                movie=movie_info,
                comments=comments,
            )
        )
    return redirect(url_for("home"))


@app.route("/login-uploader", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def loginUploader():
    if request.method == "GET":
        return render_template("signin-uploader.html")
    elif request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if not checkEmail(email):
            flash("Invalid Email or Password", "danger")
            return render_template("signin-uploader.html")

        if loginUploaderDb(email, password):
            session["logged_in"] = True
            session["is_uploader"] = True
            session["is_user"] = False
            session["email"] = email
            return redirect("/home")
        else:
            flash("Wrong username of password", "danger")
            return render_template("signin-uploader.html")


@app.route("/register-uploader", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def registerUploader():
    if request.method == "GET":
        return render_template("signup-uploader.html")
    elif request.method == "POST":
        full_name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        if checkEmailExists(email):
            flash("There is an account by this user", "danger")
            return render_template("signup-uploader.html")

        if not checkEmail(email):
            flash("Invalid Email or Password", "danger")
            return render_template("signin-uploader.html")

        if not (
            check_password_length(password) and check_password_characters(password)
        ):
            flash(
                "Invalid Password, Password should contain digits , lowercase character , upercase characters ,special characters",
                "danger",
            )
            return render_template("signup-uploader.html")

        hashed_password = hashPassword(password)
        addUploader(full_name, email, hashed_password)
        return redirect("/login-uploader")


@app.route("/upload-movie", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def uploadMovie():
    uploader_info = getInfoUploader(getUploaderId(session["email"]))
    if request.method == "GET":
        if session["is_uploader"]:
            return render_template("upload-movie.html", uploader=uploader_info)
        return "Forbidden,You dont have access to this page , Please log in"

    elif request.method == "POST":
        if not session["is_uploader"]:
            return "Forbidden,You dont have access to this page , Please log in"

        movie_name = request.form["movie_name"]
        movie_description = request.form["description"]
        rate = request.form["rate"]
        movie_image = request.files["movie_image"]
        movie_video = request.files["movie_video"]

        if not (allowed_fileImage(movie_image.filename)) or not allowed_file_sizeImage(
            movie_image
        ):
            flash("Invalid File is Uploaded", "danger")
            return render_template("upload-movie.html", uploader=uploader_info)

        if not (allowed_fileVideo(movie_video.filename)) or not allowed_file_sizeVideo(
            movie_video
        ):
            flash("Invalid File is Uploaded", "danger")
            return render_template("upload-movie.html", uploader=uploader_info)

        movie_image_url = f"uploads_posters/{movie_image.filename}"
        movie_image.save(os.path.join("static", movie_image_url))
        movie_video_url = f"uploads_videos/{movie_video.filename}"
        movie_video.save(os.path.join("static", movie_video_url))

        uploader_id = getUploaderId(session["email"])

        addMovie(
            uploader_id,
            movie_name,
            movie_description,
            rate,
            movie_image_url,
            movie_video_url,
        )
        return redirect(url_for("home"))


@app.route("/movie/<movie_id>", methods=["GET", "POST"])
def view_movie(movie_id):
    if not session["is_user"]:
        flash("Forbidden, you don't have access to this page", "danger")
        return redirect(url_for("home"))

    movie = getMovie(movie_id)
    comments = get_comments_for_movie(movie_id)

    return render_template(
        "movie_page.html",
        movie=movie,
        comments=comments,
    )


@app.route("/download/<movie_id>", methods=["GET"])
def download_video(movie_id):
    if not session["is_user"]:
        flash("Forbidden, you don't have access to this page", "danger")
        return redirect(url_for("home"))

    movie = getMovie(movie_id)

    file_path = movie[6]
    addaDownloaded(movie_id, getUserId(session["username"]))
    return send_file("static/" + file_path, as_attachment=True)


@app.route("/profile")
def profile():
    if session["is_user"]:
        user_info = getInfoUsers(getUserId(session["username"]))
        user_movies = getmoviesforUsers(getUserId(session["username"]))
        return render_template(
            "view_profile.html",
            user=user_info,
            movies=user_movies,
            commentsnumber=getcommentsNumber(),
            moviesnumber=getmoviesNumber(),
        )

    elif session["is_uploader"]:
        return redirect("/home")

    flash("You are Not Loged In", "danger")
    return redirect(url_for("loginUser"))


@app.route("/updatepassword", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def updatepassword():
    if request.method == "GET":
        return render_template("view_profile.html")
    elif request.method == "POST":
        oldpass = request.form["oldpass"]
        newpass = request.form["newpass"]
        stored_hashpassword = getInfoUsers(getUserId(session["username"]))[3]
        if checkPassMatch(stored_hashpassword, oldpass):
            flash("This is not your password.", "danger")
            return render_template("view_profile.html")
        if not (check_password_length(newpass) and check_password_characters(newpass)):
            flash(
                "Invalid Password, Password should contain digits , lowercase character , upercase characters ,special characters",
                "danger",
            )
            return render_template("view_profile.html")

        hashed_password = hashPassword(newpass)
        updateUserPassword(getUserId(session["username"]), hashed_password)
        return redirect("/home")


@app.route("/comments")
def comments():
    return redirect(url_for("comments"))


@app.route("/users")
def users():
    return redirect(url_for("users"))


@app.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("logged_in", None)
    session.pop("is_uploader", None)
    session.pop("is_user", None)
    session.pop("email", None)
    return redirect(url_for("home"))


if __name__ == "__main__":
    createUsersTable()
    createUploadersTable()
    createMoviesTable()
    createCommentsTable()
    createDownloadedTable()
    if session:
        logout()
    app.run(host="0.0.0.0", debug=True)
