from flask import Blueprint, render_template, request,session, url_for, flash, redirect, current_app, jsonify
from flask_login import login_required, current_user
from Library import app, db
from models import Books, BookRequest, Users
from sqlalchemy import func, desc
import plotly.express as px


bp = Blueprint('books', __name__)

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html")


@app.route('/userdb', methods=['GET', 'POST'])
@login_required
def userdb():
    books = Books.query.order_by(desc(Books.date_added)).all()
    return render_template("userdashboard.html", books = books)

@app.route('/sresult', methods=['GET', 'POST'])
@login_required
def sresult():
    if request.method == 'POST':
        query = request.form.get('query')
        book = Books.query.filter(
            (func.lower(Books.name).like(f"%{query.lower()}%"))  |
            (func.lower(Books.section_name).like(f"%{query.lower()}%"))  |
            (func.lower(Books.author).like(f"%{query.lower()}%")) 
            ).all()           
        return render_template("sresult.html", book=book) 
    else:
        return render_template("sresult.html")
    
@app.route('/reqbook', methods=['GET', 'POST'])
@login_required
def request_book():
    if request.method == 'POST':    
        book_id = request.form['book_id']
        user_id = request.form['user_id']
        Ndays = int(request.form['Ndays'])
        book = Books.query.get(book_id)
        existing_request = BookRequest.query.filter_by(book_id=book_id,user_id = user_id , requested=True).first()
        total_request = BookRequest.query.filter_by(user_id = user_id, requested=True).all()
        other_request = BookRequest.query.filter_by(book_id=book_id, requested=True).first()
        if existing_request:
            flash('Book already requested', category='error')
            return redirect(url_for('userdb'))
        elif len(total_request) >= 5:
            flash('User cannot request more than 5 books at once', category='error')
            return redirect(url_for('userdb'))
        elif Ndays > 7:
            flash('User cannot issue books for more than 7 days', category='error')
            return redirect(url_for('userdb'))
        elif other_request:
            flash('Book already requested by another user', category='error')
            return redirect(url_for('userdb'))
        elif book :
            new_req = BookRequest(book_id = book_id,user_id = user_id, requested = True, Ndays = Ndays)
            db.session.add(new_req)
            db.session.commit()
            flash('Book Requested', category='success')
            return redirect(url_for('userdb'))
    
    
@app.route('/userreq/<int:user_id>', methods=['GET', 'POST'])
@login_required
def userreq(user_id):
    ureq = BookRequest.query.filter_by(requested=True, approved = False, user_id = user_id)
    return render_template("showureq.html", ureq = ureq)
                

@app.route('/userissued/<int:user_id>', methods=['GET', 'POST'])
@login_required
def showuiss(user_id):
    uissued = BookRequest.query.filter_by(approved = True, user_id = user_id)
    return render_template("showuissue.html", uissued = uissued)


@app.route('/returnbook/<int:request_id>', methods=['GET','POST'])
def return_book(request_id):
        return_book = BookRequest.query.get(request_id)
        if return_book:
            db.session.delete(return_book)
            db.session.commit()
            flash('Book Returned Successfully .', category='success')
        else:
            flash('Invalid book request ID.', category='error')
        return redirect(url_for('userdb'))
    

@app.route('/showubook/<int:book_id>', methods=['GET', 'POST'])
@login_required
def showubook(book_id):
    book = Books.query.filter_by(id = book_id).all()
    return render_template("ubookcontent.html", book = book)    

@app.route('/userstats//<int:user_id>')
@login_required
def user_statistics(user_id):
    total_books_requested = BookRequest.query.filter_by(user_id=user_id, requested=True).count()
    books_borrowed = BookRequest.query.filter_by(user_id=user_id, approved=True).count()
    
    return render_template('userstats.html', current_user=current_user, total_books_requested=total_books_requested, books_borrowed=books_borrowed)