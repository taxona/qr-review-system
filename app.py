# app.py

from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Define the Review model
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.id} - {self.name}>'

# Define the Review Form using Flask-WTF
class ReviewForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    rating = SelectField('Rating', choices=[('1', '1 Star'), ('2', '2 Stars'),
                                            ('3', '3 Stars'), ('4', '4 Stars'),
                                            ('5', '5 Stars')], validators=[DataRequired()])
    comment = TextAreaField('Review', validators=[DataRequired(), Length(min=10, max=500)])
    submit = SubmitField('Submit Review')

# Home route to display reviews
@app.route('/')
def index():
    reviews = Review.query.order_by(Review.date.desc()).all()
    return render_template('index.html', reviews=reviews)

# Submit review route
@app.route('/submit', methods=['GET', 'POST'])
def submit_review():
    form = ReviewForm()
    if form.validate_on_submit():
        # Create a new review instance
        new_review = Review(
            name=form.name.data,
            rating=int(form.rating.data),
            comment=form.comment.data
        )
        try:
            db.session.add(new_review)
            db.session.commit()
            flash('Your review has been submitted successfully!', 'success')
            return redirect(url_for('prompt_external_reviews'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while submitting your review. Please try again.', 'danger')
    return render_template('submit.html', form=form)

# Prompt user to leave reviews on external platforms
@app.route('/prompt')
def prompt_external_reviews():
    return render_template('prompt.html')

# Run the app
if __name__ == '__main__':
    # Ensure the instance folder exists
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)
    # Create database tables if they don't exist
    with app.app_context():
        db.create_all()
    app.run(debug=True)
