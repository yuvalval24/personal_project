from flask import Flask, redirect, request, render_template, url_for
from flask import session as login_session
import pyrebase


app = Flask(  # Create a flask app
    __name__,
    template_folder='templates',  # Name of html file folder
    static_folder='static'  # Name of directory for static files
)
app.config["SECRET_KEY"] = "awekfhnqwepiou"

config = {
  "apiKey": "AIzaSyD1rctb8fdxnTAq_MM4m010BaZKk4NR4Go",
  "authDomain": "personal-project-seddit-y2s.firebaseapp.com",
  "databaseURL": "https://personal-project-seddit-y2s-default-rtdb.europe-west1.firebasedatabase.app",
  "projectId": "personal-project-seddit-y2s",
  "storageBucket": "personal-project-seddit-y2s.appspot.com",
  "messagingSenderId": "552845203678",
  "appId": "1:552845203678:web:3e4f353775f5bd3e398a4f",
  "measurementId": "G-M9L3JDSZ5D",
  "databaseURL" : "https://personal-project-seddit-y2s-default-rtdb.europe-west1.firebasedatabase.app"
}
firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

def vote_func():
    try:
        print(db.child('Users').get().val())
        voted0 = list(db.child('Posts').child(request.form["upvote"]).child("upvoted").get().val())
        print("voted0", voted0)
        if login_session["user"]["localId"] in voted0:
            print("voted")
        else:
            likes = db.child("Posts").child(request.form["upvote"]).child("votes").get().val()
            db.child("Posts").child(request.form["upvote"]).update({"votes":likes+1})
            user = login_session["user"]["localId"]
            db.child('Posts').child(request.form["upvote"]).update({"upvoted":voted0+[user]})
    except:
        print("downvote")


    try:
        voted1 = list(db.child('Posts').child(request.form["downvote"]).get().val())
        print(db.child("Users").get().val())
        if login_session["user"]["localId"] in voted1:
            print("voted")
        else:
            likes = db.child("Posts").child(request.form["downvote"]).child("votes").get().val()
            print(likes)
            db.child("Posts").child(request.form["downvote"]).update({"votes":likes-1})
            user = login_session["user"]["localId"]
            db.child('Posts').child(request.form["downvote"]).update({"dvoted":voted1+[user]})
    except:
        pass

@app.route("/", methods = ["get", "post"])
def home():
    if request.method == "POST":
        try:
            login_session['user'] = auth.sign_in_with_email_and_password(request.form["email-log"], request.form["password-log"])
            print("loged in succesfully")
            return redirect(url_for("home"))
        except:
            print("not sign in")


        try:
            # print(login_session["email"])
            login_session['user'] = auth.create_user_with_email_and_password(request.form["email-up"], request.form["password"])
            db.child('Users').child(login_session["user"]["localId"]).set({"email":request.form["email-up"], "password":request.form["password"], "username":request.form["username"]})
            print("signed up succesfully")
            return redirect(url_for("home"))
        except:
            print("not sign up")


        try:
            if request.form["sign out"] == "Sign Out":
                login_session.clear()
                print("cleared")
        except:
            print("not sign out")

        vote_func()
    # else:
    try:
        print(type(db.child("Posts").get().val()))
        posts = dict(db.child("Posts").get().val())
        # print("user" in list(dict(login_session).keys()))
        keys=list(posts.keys())
        keys.reverse()
        return render_template("home.html", posts=posts, keys=keys, logged=("user" in list(dict(login_session).keys())))
    except:
        return render_template("home.html", logged=("user" in list(dict(login_session).keys())))

@app.route("/submit", methods = ["get", "post"])
def submit():
    if request.method == "POST":
        try:
            user = dict(db.child("Users").child(login_session["user"]["localId"]).get().val())
            user["userId"] = login_session["user"]["localId"]
            post = {"title": request.form["title"], "text":request.form["text"], "user": user, "votes": 1, "upvoted":[""], "dvoted":[""]}
            print(post)
            db.child("Posts").push(post)
        except:
            print("not recieved")
    return render_template("submit.html", logged=("user" in list(dict(login_session).keys())))

@app.route("/posts/<string:Id>", methods = ["get", "post"])
def post(Id):
    if request.method == "GET":
        posts = dict(db.child("Posts").get().val())
        print(list(posts.keys()))
        return render_template("post.html", posts=posts, keys=list(posts.keys()), Id = Id)
    else:
        vote_func()
        posts = dict(db.child("Posts").get().val())
        print(list(posts.keys()))
        return render_template("post.html", posts=posts, keys=list(posts.keys()), Id = Id)
    return render_template("post.html", logged=("user" in list(dict(login_session).keys())))



if __name__ == "__main__":  # Makes sure this is the main process
    app.run(debug=True)
