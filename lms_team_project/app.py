from flask import Flask, render_template

app = Flask(__name__)
app.secret_key = 'hello'


@app.route("/")
def index():
    return render_template("layout.html")

app.run(debug=True)


@app.route("/login")



def login():

        return render_template("auth/login.html")






if __name__ == "__main__":
    app.run(debug=True)