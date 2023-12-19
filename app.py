# All the functions my app.py needs
import os
import datetime
import pytz
import random

from cs50 import SQL
from flask import Flask, redirect, render_template, session, request
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

# Import helper functions from helpers.py
from helpers import login_required

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies) like in pset9
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure File Uploading
app.secret_key = "thisissecret"
app.config["UPLOAD_FOLDER"] = "static/images"
app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png", ".jpeg"]
app.config["MAX_CONTENT_LENGTH"] = 3024 * 3024

# Handle cache after like in pset9
@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///maindb.db")
messagesdb = SQL("sqlite:///messages.db")

@app.route("/chat", methods=["GET", "POST"])
@login_required
def chat():
    '''Chat with owners of books to try to settle for a price/exchange'''
    ## Very similar to /requests but chat has to be from the other side
    userid = session["user_id"]
    rows = db.execute("SELECT exchanges.id, exchanges.time, users.username AS ownername, title, ownerid, method, comment, accepted FROM exchanges JOIN users ON users.id = ownerid JOIN images ON images.id = bookid WHERE buyerid = ?;", userid)
    # Change Buyerid to all the buyer usernames
    for row in rows:
        row["ownerid"] = db.execute("SELECT username FROM users WHERE id = ?;", row["ownerid"])[0]["username"]
    # Method Post
    if request.method == "POST":
        if request.form.get("send") is not None:
            message = request.form.get("chat")
            exchangeid = request.form.get("exchangeid")
            ownername = request.form.get("ownerid")
            ownerid = db.execute("SELECT id FROM users WHERE username = ?;", ownername)[0]["id"]
            messagesdb.execute("INSERT INTO messages (message, exchangeid, ownerid, buyerid, sender) VALUES (?, ?, ?, ?, ?);", message, exchangeid, ownerid, userid, userid)
        return redirect("/chat")
    else:
        # All values in messagesdb from user
        tworows = messagesdb.execute("SELECT * FROM messages WHERE buyerid = ? ORDER BY id;", userid)
        # Lists to save all the values
        messages = []
        exchangeids = []
        senders = []
        # Insert all the information into lists
        for tworow in tworows:
            messages.append(tworow["message"])
            exchangeids.append(tworow["exchangeid"])
            # If the sender == 0 it means that the sender is the buyer
            if tworow["sender"] == 0:
                senders.append(tworow["buyerid"])
            # Else the sender is the sender
            else:
                senders.append(tworow["sender"])
        # Update ids in sender to username
        for x in range(len(senders)):
            # Get the username from db
            threerows = db.execute("SELECT username FROM users WHERE id = ?;", senders[x])
            # If something went wrong and the length is not 1 like it always should be then username will be shown as N/A
            if len(threerows) != 1:
                senders[x] = "N/A"
            else:
                # Update the id to the corresponding username
                senders[x] = threerows[0]['username']
        lentworows = len(tworows)
        return render_template("/chat.html", lentworows=lentworows, rows=rows, messages=messages, exchangeids=exchangeids, senders=senders)


@app.route("/requests", methods=["GET", "POST"])
@login_required
def requests():
    '''See the requests that other people left for your books and decide if you want to reply to them'''
    userid = session["user_id"]
    # Rows with exchangeid, exchangetime, ownername, title, buyerid, method, comment and accepted
    rows = db.execute("SELECT exchanges.id, exchanges.time, users.username AS ownername, title, buyerid, method, comment, accepted FROM exchanges JOIN users ON users.id = ownerid JOIN images ON images.id = bookid WHERE ownerid = ?;", userid)
    # Change Buyerid to all the buyer usernames
    for row in rows:
        row["buyerid"] = db.execute("SELECT username FROM users WHERE id = ?;", row["buyerid"])[0]["username"]
    if request.method == "POST":
        if request.form.get("accept") is not None:
            exchangeid = request.form.get("exchangeid")
            db.execute("UPDATE exchanges SET accepted = 'TRUE' WHERE id = ?", exchangeid)
        elif request.form.get("send") is not None:
            message = request.form.get("chat")
            exchangeid = request.form.get("exchangeid")
            buyername = request.form.get("buyerid")
            buyerid = db.execute("SELECT id FROM users WHERE username = ?;", buyername)[0]["id"]
            messagesdb.execute("INSERT INTO messages (message, exchangeid, ownerid, buyerid, sender) VALUES (?, ?, ?, ?, ?);", message, exchangeid, userid, buyerid, userid)
        return redirect("/requests")
    else:
        # All values in messagesdb from user
        tworows = messagesdb.execute("SELECT * FROM messages WHERE ownerid = ? ORDER BY id;", userid)
        # Lists to save all the values
        messages = []
        exchangeids = []
        senders = []
        # Insert all the information into lists
        for tworow in tworows:
            messages.append(tworow["message"])
            exchangeids.append(tworow["exchangeid"])
            # If the sender == 0 it means that the sender is the buyer
            if tworow["sender"] == 0:
                senders.append(tworow["buyerid"])
            # Else the sender is the sender
            else:
                senders.append(tworow["sender"])
        # Update ids in sender to username
        for x in range(len(senders)):
            # Get the username from db
            threerows = db.execute("SELECT username FROM users WHERE id = ?;", senders[x])
            # If something went wrong and the length is not 1 like it always should be then username will be shown as N/A
            if len(threerows) != 1:
                senders[x] = "N/A"
            else:
                # Update the id to the corresponding username
                senders[x] = threerows[0]['username']
        lentworows = len(tworows)
        return render_template("/requests.html", lentworows=lentworows, rows=rows, messages=messages, exchangeids=exchangeids, senders=senders)

@app.route("/myprofile", methods=["GET", "POST"])
@login_required
def myprofile():
    userid = session["user_id"]
    '''See all your profile settings and possibility to delete your profile'''
    # Select all the important values to render into template from table users
    rows = db.execute("SELECT * FROM users WHERE id = ?;", userid)
    if request.method == "POST":
        # Change Password button was pressed
        if request.form.get("changepwd") is not None:
            ## Check for pwd input
            # Check if password is blank
            if not request.form.get("password"):
                return render_template("myprofile.html", rows=rows, error="Please enter valid password")
            # Check if passwords match
            elif request.form.get("password") != request.form.get("confirmation"):
                return render_template("myprofile.html", rows=rows, error="Passwords didn't match")
            # Password shouldn't be longer than 20 characters
            elif len(request.form.get("password")) > 20:
                return render_template("myprofile.html", rows=rows, error="Password is too long")
            # Password is okay and can be updated in db
            hashpassword = generate_password_hash(request.form.get("password"))
            db.execute("UPDATE users SET hash = ? WHERE id = ?;", hashpassword, userid)
            # Return to myprofile with successmessage
            return render_template("/myprofile.html", rows=rows, message="Password was changed successfully")
        # Delete Account Button was pressed
        elif request.form.get("deleteacc") is not None:
            ### Delete account and log out
            ## Delete chats from user for all the ownerids' and buyerids
            messagesdb.execute("DELETE FROM messages WHERE ownerid = ? OR buyerid = ?;", userid, userid)
            ## Delete everything from user in table exchanges
            db.execute("DELETE FROM exchanges WHERE ownerid = ? OR buyerid = ?;", userid, userid)
            ## Delete user from table users
            db.execute("DELETE FROM users WHERE id = ?;", userid)
            # Delete all the images in static/images folder
            rows = db.execute("SELECT path FROM images WHERE userid = ?;", userid)
            for row in rows:
                try:
                    os.remove(row["path"])
                except:
                    return render_template("/delete.html", error="an error occured, please try again")
            ## Delete everything from user in table images
            db.execute("DELETE FROM images WHERE userid = ?;", userid)
            # Clear session
            session.clear()
            # Redirect to homepage logged out
            return redirect("/")

        # Just for safety
        else:
            return render_template("error.html")
    # Method Get
    else:
        return render_template("/myprofile.html", rows=rows)

@app.route("/contact", methods=["GET", "POST"])
@login_required
def contact():
    # Exchangeid of current session so redirected from /exchange
    exchangeid = session["contact"]
    # If not redirected from /exchange so session is empty then render Error
    if exchangeid is None:
        return render_template("error.html")
    else:
        # Get all the important information from users.db
        rows = db.execute("SELECT exchanges.id AS exchangeid, exchanges.time AS exchangetime, ownerid, buyerid, bookid, method, username AS ownername, title, author, description, path FROM exchanges JOIN users ON users.id = ownerid JOIN images ON images.id = bookid WHERE exchangeid = ?;", exchangeid)
        # Method Post
        if request.method == "POST":
            # See if there is already a comment so user can only send one
            commentnull = db.execute("SELECT comment FROM exchanges WHERE id = ?;", exchangeid)
            if commentnull[0]["comment"] is None:
                # Get comment from form
                comment = request.form.get("comment")
                # Update exchanges table
                db.execute("UPDATE exchanges SET comment = ? WHERE id = ?;", comment, exchangeid)
                # Get values to insert into message table
                ownerid = db.execute("SELECT ownerid FROM exchanges WHERE id = ?;", exchangeid)[0]["ownerid"]
                buyerid = db.execute("SELECT buyerid FROM exchanges WHERE id = ?;", exchangeid)[0]["buyerid"]
                # Insert into message table in messages database
                messagesdb.execute("INSERT INTO messages (message, exchangeid, ownerid, buyerid) VALUES (?, ?, ?, ?);", comment, exchangeid, ownerid, buyerid)
                # Clear session after using it
                session.pop("comment", None)
                # Show user that it worked with message
                return render_template("/contact.html", message="""Your message has been sent. See if the owner answered you in "Chat with owners" section""")
            else:
                # Clear session after using it
                session.pop("comment", None)
                return render_template("/error.html", error="You already sent a message!")
        else:
            return render_template("/contact.html", rows=rows)

@app.route("/exchange", methods=["GET", "POST"])
@login_required
def exchange():
    '''See all the different exchanges you saved'''
    # Method Post
    if request.method == "POST":
        # Get id for the exchange
        exchangeid = request.form.get("exchangeid")
        # Delete button means delete exchange
        if request.form.get("delete") is not None:
            db.execute("DELETE FROM exchanges WHERE id = ?;", exchangeid)
            messagesdb.execute("DELETE FROM messages WHERE exchangeid = ?;", exchangeid)
            return redirect("/exchange")
        # Contact button saves exchangeid in session and redirects to /contact
        elif request.form.get("contact") is not None:
            session["contact"] = exchangeid
            return redirect("/contact")
        # Shouldn't happen just for safety
        else:
            return render_template("error.html")
    # Method Get
    else:
        # Userid of current session
        userid = session["user_id"]
        # This gets all the SELECTED items from table images and additionally the username of the corresponding user from table users
        rows = db.execute("SELECT exchanges.id as exchangeid, title, exchanges.time, username, ownerid, buyerid, method, path, description, author FROM images JOIN exchanges ON images.id = bookid JOIN users ON images.userid = users.id WHERE buyerid = ?;", userid)
        return render_template("/exchange.html", rows=rows)

@app.route("/browse", methods=["GET", "POST"])
@login_required
def browse():
    '''Browse books that other users are selling/exchanging and have the opportunity to buy/exchange it'''
    # Method Post
    if request.method == "POST":
        # Get all the relevant values
        buyerid = session["user_id"]
        bookid = request.form.get("bookid")
        ownerid = request.form.get("ownerid")
        time = datetime.datetime.now(pytz.timezone("Europe/Berlin"))

        # Check first if buyer already tried to request buy/exchange
        rows = db.execute("SELECT * FROM exchanges WHERE ownerid = ? AND buyerid = ? AND bookid = ?;", ownerid, buyerid, bookid)
        if len(rows) == 1:
            return render_template("error.html", error="You already tried to buy/exchange this book")
        else:
            # Buy button was pressed
            if request.form.get("buttonbuy") is not None:
                # Insert into exchanges
                method = "buy"
                db.execute("INSERT INTO exchanges (time, buyerid, method, bookid, ownerid) VALUES (?, ?, ?, ?, ?);", time, buyerid, method, bookid, ownerid)
                return redirect("/exchange")
            # Exchange button was pressed
            elif request.form.get("buttonexchange") is not None:
                method = "exchange"
                db.execute("INSERT INTO exchanges (time, buyerid, method, bookid, ownerid) VALUES (?, ?, ?, ?, ?);", time, buyerid, method, bookid, ownerid)
                return redirect("/exchange")
            else:
                return render_template("error.html")

    # Method Get
    else:
        # Display all the Books that are in database except the books of the user (table image)
        userid = session["user_id"]
        # This gets all the SELECTED items from table images and additionally the username of the corresponding user from table users
        rows = db.execute("SELECT images.id, title, author, description, path, userid, time, username FROM images JOIN users ON images.userid = users.id WHERE NOT userid = ?;", userid)
        return render_template("/browse.html", rows=rows)


@app.route("/delete", methods=["GET", "POST"])
@login_required
def delete():
    '''Delete and entry of a user'''
    if request.method == "POST":
        if not request.form.get("deletepath"):
            return render_template("/delete.html", error="an error1 occured")
        else:
            # Imagepath
            deletepath = request.form.get("deletepath")
            # Only delete it if it is from the active user
            userid = session["user_id"]
            rows = db.execute("SELECT id FROM images WHERE path = (?) AND userid = ?;", deletepath, userid)
            if len(rows) != 1:
                return render_template("/delete.html", error="an error2 occured")
            else:
                imageid = rows[0]["id"]
                # Delete it in the database table exchanges
                db.execute("DELETE FROM exchanges WHERE bookid = ?;", imageid)
                # Delete it in the database table images
                db.execute("DELETE FROM images WHERE id = ?;", imageid)
                # Delete it from the folder
                try:
                    os.remove(deletepath)
                except:
                    return render_template("/delete.html", error="an error3 occured")

            return render_template("/delete.html", success="Entry Deleted")
    else:
        return render_template("/delete.html")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    '''Upload pictures and describe the book that you want to sell'''
    if request.method == "POST":
        ## Boxes filled in
        # Title
        if not request.form.get("title"):
            return render_template("/sell.html", titleerror="Please enter valid title")
        # Author
        elif not request.form.get("author"):
            return render_template("/sell.html", authorerror="Please enter valid author")
        # Description
        elif not request.form.get("description"):
            return render_template("/sell.html", descriptionerror="Please enter valid description")

        else:
            # Make sure file was loaded correctly
            if "file" not in request.files:
                return render_template("/sell.html", imageerror1="File could not be uploaded")
            ## Image has right format
            # Request the image
            file = request.files["file"]
            oldimagename = secure_filename(file.filename)
            # Get image extension
            image_ext = os.path.splitext(oldimagename)[1]
            # Generate a random name for the image
            imagename = str(random.randint(0, 9999999999999)) + image_ext

            if image_ext not in app.config["UPLOAD_EXTENSIONS"]:
                return render_template("/sell.html", imageerror1="File type is not allowed")

            file.save(os.path.join(app.config["UPLOAD_FOLDER"], imagename))
            # Insert into db
            path = "static/images/" + imagename
            userid = session["user_id"]
            time = datetime.datetime.now(pytz.timezone("Europe/Berlin"))
            db.execute("INSERT INTO images (title, author, description, path, userid, time) VALUES (?, ?, ?, ?, ?, ?);", request.form.get("title"), request.form.get("author"), request.form.get("description"), path, userid, time)

        return redirect("/sell")
    else:
        userid = session["user_id"]
        ## Display all the already uploaded pictures of the user
        # Get all the paths from the images of the user
        rows = db.execute("SELECT path, title, author, description FROM images WHERE userid = ?;", userid)
        return render_template("/sell.html", rows=rows)

@app.route("/")
def index():
    '''This is the main page where the user should be introduced to the website'''
    return render_template("/index.html")

@app.route("/logout")
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login
    return redirect("/")

@app.route("/tac.html")
def tac():
    '''Renders terms and conditions'''
    return render_template("tac.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # If method is POST
    if request.method == "POST":
        ## Check if all the boxes are filled correctly
        # Check if email is blank
        if not request.form.get("useremail"):
            return render_template("register.html", emailerror="Please enter valid e-mail")
        # Check if username is blank
        elif not request.form.get("username"):
            return render_template("register.html", usernameerror="Please enter valid username")
        # Check if password is blank
        elif not request.form.get("password"):
            return render_template("register.html", passworderror="Please enter valid password")
        # Check if passwords match
        elif request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", confirmationerror="Passwords didn't match")
        # Check if checkbox is checked ##This is just for fun##
        #elif not request.form.get("checkbox"):
           #return render_template("register.html", checkboxerror="You have to Agree to the Terms and Conditions to register")

        # Is the user and email already registered?
        usernamebool = db.execute(
            "SELECT * FROM users WHERE EXISTS (SELECT username FROM users WHERE username = ?);",
            request.form.get("username"),
        )
        useremailbool = db.execute(
            "SELECT * FROM users WHERE EXISTS (SELECT email FROM users WHERE email = ?);",
            request.form.get("useremail"),
        )

        # If already registered, load /register with error
        if usernamebool:
            return render_template("register.html", usernameerror2="Username already exists.")
        elif useremailbool:
            return render_template("register.html", emailerror2="Email already exists.")
        # Password shouldn't be longer than 20 characters
        elif len(request.form.get("password")) > 20:
            return render_template("register.html", passworderror="Password is too long")
        # If all is okay hash password and insert all into database
        else:
            useremail = request.form.get("useremail")
            username = request.form.get("username")
            hashpassword = generate_password_hash(request.form.get("password"))
            db.execute(
                "INSERT INTO users (email, username, hash) VALUES(?, ?, ?);",
                useremail,
                username,
                hashpassword,
            )
            return render_template("login.html")

    # If method get then render register.html normally
    else:
        return render_template("register.html")

# This is slightly modified but like in pset9
@app.route("/login", methods=["GET", "POST"])
def login():
    # Clear any session that is open
    session.clear()

    # Method Post
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", usernameerror="Please enter username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", passworderror="Please enter password")

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return render_template("login.html", botherror="password and/or username wrong")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # Method Get
    else:
        return render_template("login.html")
