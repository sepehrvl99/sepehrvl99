from flask import Flask, render_template


app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/index.html")
def home_page():
    return render_template("index.html")


@app.route("/about.html")
def about_page():
    return render_template("about.html")

@app.route("/Doctor.html")
def doctor_page():
    return render_template("doctor.html")

@app.route("/services.html")
def services_page():
    return render_template("services.html")

@app.route("/dep.html")
def dep_page():
    return render_template("dep.html")

@app.route("/elements.html")
def elements_page():
    return render_template("elements.html")

@app.route("/blog.html")
def blog_page():
    return render_template("blog.html")

@app.route("/single-blog.html")
def single_blog_page():
    return render_template("single-blog.html")

@app.route("/contact.html")
def contact_page():
    return render_template("contact.html")


if __name__ == "__main__":
    app.run(debug=True)
