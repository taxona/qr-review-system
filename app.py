from flask import Flask, render_template, request, redirect, url_for, flash
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length
import os
from datetime import datetime
from flask_mail import Mail, Message

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
mail = Mail(app)

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    comment = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Review {self.id} - {self.name}>'

class ReviewForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    rating = SelectField('Rating', choices=[('1', '1 Star'), ('2', '2 Stars'),
                                            ('3', '3 Stars'), ('4', '4 Stars'),
                                            ('5', '5 Stars')], validators=[DataRequired()])
    comment = TextAreaField('Review', validators=[DataRequired(), Length(min=10, max=500)])
    # Uncomment below if implementing reCAPTCHA
    # recaptcha = RecaptchaField()
    submit = SubmitField('Submit Review')

@app.route('/')
def index():
    reviews = Review.query.order_by(Review.date.desc()).all()
    return render_template('index.html', reviews=reviews)

@app.route('/submit', methods=['GET', 'POST'])
def submit_review():
    form = ReviewForm()
    if form.validate_on_submit():
        new_review = Review(
            name=form.name.data,
            rating=int(form.rating.data),
            comment=form.comment.data
        )
        try:
            db.session.add(new_review)
            db.session.commit()
            # Send email notification
            msg = Message('New Review Submitted',
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[app.config['ADMIN_EMAIL']])
            msg.body = f'Name: {new_review.name}\nRating: {new_review.rating}\nComment: {new_review.comment}'
            mail.send(msg)
            flash('Your review has been submitted successfully!', 'success')
            return redirect(url_for('prompt_external_reviews'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while submitting your review. Please try again.', 'danger')
    return render_template('submit.html', form=form)

@app.route('/prompt')
def prompt_external_reviews():
    return render_template('prompt.html')

if __name__ == '__main__':
    os.makedirs(os.path.join(app.instance_path), exist_ok=True)
    with app.app_context():
        db.create_all()
    app.run(debug=True)
