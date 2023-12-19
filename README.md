# Uni Freiburg Bookexchange
#### Video Demo: https://youtu.be/365Hj8-bICg
#### Description:

A web-base application that allows users to sell and exchange books to each other that they dont need anymore.

For testing purposes there is the account user1 with password: 1234

For understanding of use please watch the video provided.

# Introduction
In the start I will go through every major keystone of this webapp and explain the use and my thought process behind making it.
This webapp is based on flask which is why the main elements are the app.py, helpers.py, the two databases, the templates folder and the static folder with /images and the styles.css file.
## app.py
In app.py you can first see all the imported frameworks and functions which I needed for the project. One of the most important ones are render_template, used in almost every app.route and login_required imported from helpers which allows the user to request a certain route only when he is logged in.

Instead of cookies this webapp uses a filesystem like in pset9 to be used by session:
``` python
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
```

In addition to that the app also had to configured for File Uploading, to upload images to the static/images file for the books you want to put on the webapp for selling/exchangeing.
``` python
app.secret_key = "thisissecret"
app.config["UPLOAD_FOLDER"] = "static/images"
app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png", ".jpeg"]
app.config["MAX_CONTENT_LENGTH"] = 3024 * 3024
```

I will explain the routes and functions of app.py later in this markdown.

## helpers.py
helpers.py just contains one function "login_required()" and all the necessary imports for it. This function, from pset9(finance) is used to ensure only logged in users can access the main pages of the website which makes it a security risk if it is not implemented right.

Other helper functions were not created for this webapp, because I was able to just implement them right in the app.py file, and they were mostly specific for the route where they were used.

## Databases
### maindb.db
The main database contains three important tables:
* users
* images
* exchanges

All the important information about the users, like id, email, username, and hash, are stored in the users table. As you can see in the schema, the id is AUTOINCREMENTed which means that i dont have to worry about assigning an id and all the ids will differ.

For the images (which also means for the books) I needed general Information from the user and additionally the path where I will store the image. Of course I needed also the user id to know who uploaded the image/book.

The exchanges table stores all the important values I need for the data collection about exchanges of books. With the information stored here, I can know who wants to buy what from whom with which method and wether they commented something and if the owner has accepted the request.

Once the owner accepted the request, both the owner and the buyer will see a Chat where they can communicate to each other, which brings me to messages.db

### messages.db
The reason why I made a seperate database containing all the messages is just the amount of Chats and data that might be put into this. If there is any problem with the amounts of data in the messages table, then I wouldn't want to put my data from main database at risk, so I created a new database.

Additionally I can delete all the Chats whenever I want without having to access the database. I can just delete the file. This would make it easy to reset the Chats, if the Data becomes to big.

## /static
The static folder contains all the images that the users upload and also the background picture of index.html, the logo which was created with wix.com and the stylesheet.

Logo: ![image](static/Logo_madewith_wix.com.png)
source: wix.com

background: ![image](static/background.jpg)
source: https://www.urbanite.net/wp-content/uploads/2022/03/elsa-asenijeff-und-ich-will-frei-stolz-und-allein-mein-leben-aufrecht-tragen-1024x577.jpg

The stylesheet was implemented throughout the development process but the main aspects of the webapp which it is responsible for are the navbar, the cards that display the books with their information and almost all the forms and buttons. They were all taken from bootstrap.com and modified to fit into the design and use of the webapp.

## /templates
There are a lot of templates for the webapp which is why I decided to summarize them into groups:
* Homepage
    * layout.html
    * index.html
    * tac.html
* Profile
    * register.html
    * login.html
    * myprofile.html
* Books
    * browse.html
    * sell.html
    * exchange.html
    * delete.html
* Chat
    * contact.html
    * requests.html
    * chat.html
* Others
    * error.html

I will explain the functionality of these together with the functionality of app.py in "Main Part"

### Homepage
These templates build the homepage and additionally the terms and conditions (tac.html) are just a template I found from the internet and is just there for fun. It is not legally binding and doesn't have to be accepted.

### Profile
In these templates the user can create a profile, change their password and also delete it. Deleting it will cause all the data from the user to be deleted. The implementation of login and register are similar to pset9 but modified to fit my webapp better.

### Books
This is for the uploading and displaying of the book cards. Delete.html is just there for the deleting of an entry and showing the user if the deleting worked.

### Chat
On these pages the user can communicate with potential buyers and also with owners of books they want to buy/exchange. In brows.html, all uploaded books are being displayed.

### Others
The error.html template was just made for the occasion of any error which every function can render to display another error.




# Main Part
Here I will explain the routes and their templates more in depth.
## Homepage
### layout.html
Layout.html is the template for all other templates. Here you can see the implementation of the navbar with bootstrap and also the Logo. Like in pset9 you are only able to see the special navbar when logged in. Otherwise you can only access register.html, login.html and index.html.
Also notice two dropdown menus that make the overview of the navbar a lot cleaner.
In the main tag there will be the extension of all other templates.
### index.html
This is the first page of the website that the user will see so I wanted to make it look especially well.
The function of index in @app.route("/logout") is only a render_template because I don't need a special function for the index page to look good.
### tac.html
As mentioned this is just a free template I found on the internet and is just there for fun.


## Profile
### register.html
Like in almost every route you can find the differantiation wether the user came to this route with the method post or the method get. With the method get only the template gets rendered. That means the user sees all the input forms and the buttons which he has to fill.
If the method is post, the user pressed the button which has the type submit to submit the whole form.
Every input tag has the required attribute. This isn't save because they could just delete it out of their browser and post it anyway. That is why I implemented the function register() to check again if all boxes are not empty (if they are there will be an errormessage rendered to reflect to the user what they did wrong).
Afterwards the username and email will be checked so no email or username will appear twice on the webapp. Otherwise users couldn't know if they wrote with the same person when exchanging books.

After checking all the important aspects of the registration, the posted input (password as hash; this will make sure that even I wont know which password the user has) will be saved in maindb.db table users and the login.html template will be loaded.

### login.html
The most interesting part here is probably the check of the password and the saving of the userid in session["user_id"] to always have access to the userid from the user that is currently logged in. This will become important in the implementation of books and chat.

### myprofile.html
Here the user can see his own email and username. This is implemented by calling the database values into the variable rows. This will be sent to the template and can be iterated over with JINJA code. Likewise was it executed in a lot of other templates, whenever the user sees information from a database.

With the use of a form the user can post their new desired password and change it in the database. Again there is the attribute required and also a second check by the function myprofile() in app.py.

The delete account button is listened to by this line of code:
```
elif request.form.get("deleteacc") is not None:

```
Likewise was listened for the change password button.

When the delete button is pressed it will first delete from all tables that reference the users table and then the users table because otherwise there will be a FOREIGN KEY ERROR.

Additionally there is the javascript function as the attribute onclick which will confirm the choice of the user to delete the account, so they don't delete their account if they only press it accidentally.

## Books
### browse.html
Like mentioned the information of the database relevant for browse.html, so everything from table images in maindb.db, is called into variable rows and iterated over with JINJA code. Everything here means all books that are not uploaded by the current usersession, because they should not be able to buy their own books.

A form with hidden values was made to be able to get the specific information about one entry with
```
request.form.get("informationid")
```
This enables the use of only one function (browse()) to execute the buy button and the exchange button.
When a button is pressed all the information is inserted into the table exchanges from maindb.db. Only the method differs but later we can recall which method the user chose.
### sell.html
This implementation was the most tricky part together with the implementation of Chat. The challenge was to get a file through an html form and only allow certain types of image files and also limit the size of the files.
This was achieved through the already displayed code in app.py:
``` python
app.secret_key = "thisissecret"
app.config["UPLOAD_FOLDER"] = "static/images"
app.config["UPLOAD_EXTENSIONS"] = [".jpg", ".png", ".jpeg"]
app.config["MAX_CONTENT_LENGTH"] = 3024 * 3024
```
This declares the upload folder, the extensions that are allowed and the limit to the file size.

In sell() you can see the use of "os" that allows the interaction with the operating system through python. The extension is being checked through:
``` python
# Request the image
file = request.files["file"]
oldimagename = secure_filename(file.filename)
# Get image extension
image_ext = os.path.splitext(oldimagename)[1]
# Generate a random name for the image
imagename = str(random.randint(0, 9999999999999)) + image_ext

if image_ext not in app.config["UPLOAD_EXTENSIONS"]:
    return render_template("/sell.html", imageerror1="File type is not allowed")
```
Also this gives the image a random number as name to make sure that we can always get the same image and not dependent on the image name that the user chose to upload.

Furthermore you can see all the books you have already uploaded. The db.execute function looks for all the books / images that the userid from current session has uploaded and loads them into the variable rows which then can be iterated in sell.html. The form in which the delete button is found has the action /delete which means this is calling the /delete route. This was implemented in this way because I wanted to load a Delete message anyways after deleting an entry, so it was easy to also make the form post to /delete.

The only hidden value here is the image path of the book because all the information about the book will be stored in the same row of the table and we need the path anyway to delete the image from the folder /images in /static.

### delete.html
The delete HTML just shows an error or an success but the function in app.py is more interesting. The interesting part here is the try to delete part:
``` python
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
```
This was made in this way because the path might be not working so this might make a huge error. That's why I decided to try deleting the image file and if it doesn't work just show an error message on /delete.html to prevent an unexpected Error to happen.

### exchange.html
In exchange.html all the books that the user might buy/exchange are displayed, again through a modified variable rows which gets the wanted values of the database.
Again the user has the option to delete a card if they are not interested anymore. The buttons are differentiated through the same logic as in ### myprofile.html.

Additionally the user has the option to contact the user, where the exchangeid (the id for this specific exchange) will be saved in a session["contact"] to be able to use it in route /contact, where the user is redirected to.

## Chat
### contact.html
In contact.html the user was redirected from exchange.html. The function contact() inserts a first message into table messages from messages.db and is the first chat contact between two users. After using the session["contact"] it will be pop ped to free it whenever it is not used. Otherwise there could be errors if a session is not being updated and the buyer might contact the wrong owner.
``` python
# Clear session after using it
session.pop("comment", None)
```


### requests.html
Here is the first implementation of the Chat. Here the user can see all the requests he got from other users that used exchange.html and contact.html for his book. First he will be asked to accept the request, otherwise the chat will not be started with the owner. After the user accepts by pressing the accept button, thus updating the column accepted from table exchanges to true which is by default false (== 0). The template is implemented with an if else JINJA function, so it checks wether a row has the value accepted = 0 or != 0. depending on that the chat will be opened for the owner:
```
{% if row["accepted"] == 0 %}
    <div id="panelsStayOpen-collapse{{ row["id"] }}" class="accordion-collapse collapse">
        <form action="/requests" method="post">
            <br>
            <input type="hidden" name="exchangeid" value="{{ row["id"] }}">
            <button name="accept" class="btn btn-success" type="submit">Accept request</button>
            <br>
        </form>
    </div>
    {% else %}
    <div id="panelsStayOpen-collapse{{ row["id"] }}" class="accordion-collapse collapse">
        <div class="accordion-body">
            <div class="scrollbox">
                {% for x in range(lentworows) %}
                    {% if exchangeids[x] == row["id"] %}
                        <p>{{ senders[x] }}: {{ messages[x] }}</p>
                        <br>
                    {% endif %}
                {% endfor %}
            </div>
        </div>
        <form action="/requests" method="post" class="form-inline">
            <div class="chatinput">
                <div class="cell">
                    <input type="hidden" name="exchangeid" value="{{ row["id"] }}">
                    <input type="hidden" name="ownerid" value="{{ row["ownerid"] }}">
                    <input type="hidden" name="buyerid" value="{{ row["buyerid"] }}">
                    <input name="chat" class="form-control" type="text" placeholder="Chat" required>
                </div>
                <div class="cell">
                    <button name="send" class="btn btn-dark" type="submit">Send</button>
                </div>
            </div>
        </form>
    </div>
{% endif %}
```
The structure of the chats is an accordion also based on bootstrap and modified with own implemented scrollboxes to make the chat more overviewable.



### chat.html
Chat.html is essentially the same as requests.html just without the accept button because the user wants to buy / exchange a book from someone and don't sell / exchange to someone.
Thats why you can see at most parts that the buyerid and ownerid will be switched.

# Conclusion
This was a very fun project and I hope i will be able to continue working on it and maybe even put it online so other people of Uni Freiburg will be able to use it. I have faced a lot of challenges with this project and also feel like that I understand flask, html, css and python more now and can build on this knowledge.
