'''
A Web application that shows Google Maps around schools, using
the Flask framework, and the Google Maps API.
'''

from flask import Flask, render_template, abort
app = Flask(__name__)


class School:
    def __init__(self, key, name, lat, lng):
        self.key  = key
        self.name = name
        self.lat  = lat
        self.lng  = lng

schools = (
    School('sit',      'Stevens Institute Of Technology',   40.7439478, -74.0381506),
)
schools_by_key = {school.key: school for school in schools}


@app.route("/")
def index():
    return render_template('index.html', schools=schools)


@app.route("/<school_code>")
def show_school(school_code):
    school = schools_by_key.get(school_code)
    if school:
        return render_template('map.html', school=school)
    else:
        abort(404)

app.run(host='localhost', debug=True)
