from flask import Blueprint, render_template, request,session, url_for, flash, redirect, current_app, jsonify
import plotly.express as px
from models import Admin, Section, Books, Users, BookRequest
from flask_bcrypt import check_password_hash
from Library import db, bcrypt, app
from sqlalchemy import func
from datetime import datetime



bp = Blueprint('admin', __name__)

#admin = Admin(username = 'Pratik1999Jha', password = bcrypt.generate_password_hash('Hello2020',10))
#db.session.add(admin)
#db.session.commit()


@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == "" and password == "":
            flash('Please fill in all the fields', 'danger')
            return redirect(url_for('adminlogin'))
        else:
            admins = Admin.query.filter_by(username=username).first()
            if admins and bcrypt.check_password_hash(admins.password, password):
                session['admin_id'] = admins.id
                session['admin_username'] = admins.username
                ct = datetime.now()
                books = BookRequest.query.filter_by(approved = True)
                for i in books:
                    if ct > i.date_return :
                        i.approved = False
                db.session.commit()
                flash('Logged In Successfully', category='success')
                return redirect(url_for('admindashboard'))
            else:
                flash('Invalid Email or Password', category='error')
                return redirect(url_for('adminlogin'))
    
    return render_template("adminlogin.html", title = "Admin Login")


@app.route('/adminlogout')
def adminlogout():
    if not session.get('admin_id'):
        return redirect(url_for('home'))
    if session.get('admin_id'):
        session['admin_id'] = None
        session['admin_username'] = None
        flash('Logged Out Successfully', category='success')
        return redirect(url_for('adminlogin'))


@app.route('/admindb', methods=['GET', 'POST'])
def admindashboard():
    if ('admin_id' in session):
        dashboard = True
        secs = Section.query.all()
        return render_template("admindb.html", dashboard = dashboard, secs =secs)
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))


@app.route('/addsection', methods=['GET', 'POST'])
def addsection():
    if ('admin_id' in session):
        dashboard = True
        if request.method == 'POST':
            name = request.form['name']
            desc = request.form['desc']
            
            secs = Section.query.filter_by(name = name).first()
            if secs:
                flash('Section already exists.', category='error')
            else:
                new_secs = Section(name = name, desc = desc)
                db.session.add(new_secs)
                db.session.commit()
                flash('New Section Created!', category='success')
                return redirect(url_for('admindashboard'))
        return render_template("addsection.html", dashboard = dashboard)
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))
    
@app.route('/addbook/<string:name>', methods=['GET', 'POST'])
def addbook(name):
    if ('admin_id' in session):
        dashboard = True
        if request.method == 'POST':
            bname = request.form['bname']
            author = request.form['author']
            content = request.form['content']
            
            book = Books.query.filter_by(name = bname).first()
            if book:
                flash('Book in this Section already exists.', category='error')
            else:
                new_book = Books(name = bname, author = author, content = content, section_name = name)
                db.session.add(new_book)
                db.session.commit()
                flash('New Book Added!', category='success')
                return redirect(url_for('admindashboard'))
        return render_template("addbook.html", dashboard = dashboard)
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))
    
@app.route('/showsec/<string:name>', methods=['GET', 'POST'])
def showsec(name):
    if ('admin_id' in session):
        dashboard = True
        book = Books.query.filter_by(section_name = name).all()
        return render_template("showsec.html", dashboard = dashboard, book = book, name = name)    
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))
            
@app.route('/deletesec/<string:name>', methods=['GET', 'POST'])
def deletesec(name):
    if ('admin_id' in session):
        dashboard = True    
        secs = Section.query.filter_by(name = name).first()                
        db.session.delete(secs)
        db.session.commit()
        flash('Section Deleted!', category='success')
        return render_template("admindb.html", dashboard = dashboard)
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))


@app.route('/showusers', methods=['GET', 'POST'])
def showusers():
    if ('admin_id' in session):
        dashboard = True
        users = Users.query.all()
        return render_template("showusers.html", dashboard = dashboard, users = users)
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))
    

@app.route('/showbreq', methods=['GET', 'POST'])
def showbreq():
    if ('admin_id' in session):
        dashboard = True
        breq = BookRequest.query.filter_by(requested=True, approved = False)
        return render_template("showreq.html", dashboard = dashboard, breq = breq)
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))


@app.route('/approvereq/<int:request_id>', methods=['GET','POST'])
def approve_request(request_id):
    if 'admin_id' in session:
        dashboard = True
        request_to_approve = BookRequest.query.get(request_id)
        if request_to_approve:
            request_to_approve.approve()
            db.session.commit()
            flash('Book request approved.', category='success')
        else:
            flash('Invalid book request ID.', category='error')
        return redirect(url_for('showbreq'))
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))
    
@app.route('/denyreq/<int:request_id>', methods=['GET','POST'])
def deny_request(request_id):
    dashboard = True
    if 'admin_id' in session:
        request_to_deny = BookRequest.query.get(request_id)
        if request_to_deny:
            db.session.delete(request_to_deny)
            db.session.commit()
            flash('Book request denied.', category='success')
        else:
            flash('Invalid book request ID.', category='error')
        return redirect(url_for('showbreq'))
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))

@app.route('/showbooksiss', methods=['GET', 'POST'])
def showbiss():
    if ('admin_id' in session):
        dashboard = True
        bissued = BookRequest.query.filter_by(approved = True)
        return render_template("adshowbissued.html", dashboard = dashboard, bissued = bissued)
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))


@app.route('/issuerevoke/<int:request_id>', methods=['GET','POST'])
def revoke_access(request_id):
    dashboard = True
    if 'admin_id' in session:
        revoke_access = BookRequest.query.get(request_id)
        user = Users.query.get(revoke_access.user_id)
        if revoke_access:
            db.session.delete(revoke_access)
            db.session.commit()
            flash(f'Book Access Revoked for {user.username}.', category='success')
        else:
            flash('Invalid book request ID.', category='error')
        return redirect(url_for('showbiss'))
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))
    
@app.route('/removeuser/<int:user_id>', methods=['GET','POST'])
def removeuser(user_id):
    dashboard = True
    if 'admin_id' in session:
        remove_user = Users.query.get(user_id)
        if remove_user:
            db.session.delete(remove_user)
            db.session.commit()
            flash(f'{remove_user.username} removed from the Library Database.', category='success')
        return redirect(url_for('showusers'))    
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))
    
@app.route('/deletebook/<int:book_id>', methods=['GET','POST'])
def deletebook(book_id):
    dashboard = True
    if 'admin_id' in session:
        delete_book = Books.query.get(book_id)
        if delete_book:
            db.session.delete(delete_book)
            db.session.commit()
            flash(f'Book "{delete_book.name}" has been removed from the Library Database.', category='success')
        return redirect(url_for('admindashboard'))    
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))
    
@app.route('/updatebook/<int:book_id>', methods=['GET','POST'])
def updatebook(book_id):
    dashboard = True
    if 'admin_id' in session:
        update_book = Books.query.get(book_id)
        section = Section.query.all()
        if request.method == 'POST':
            name = request.form['name']
            author = request.form['author']
            section_name = request.form['section']
        
            if not name or not author or not section_name:
                flash('All fields are required.', 'error')
                return redirect(url_for('updatebook', book_id=book_id))
            
            update_book.name = name
            update_book.author = author
            update_book.section_name = section_name
        
            db.session.commit()
            return redirect(url_for('showsec', name=section_name))
        return render_template('adupdatebook.html', update_book=update_book, section=section, dashboard = dashboard)
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))
    
@app.route('/adresult', methods=['GET', 'POST'])
def adresult():
    dashboard = True
    if 'admin_id' in session:
        if request.method == 'POST':
            query = request.form.get('query')
            book = Books.query.filter(
                (func.lower(Books.name).like(f"%{query.lower()}%"))  |
                (func.lower(Books.section_name).like(f"%{query.lower()}%"))  |
                (func.lower(Books.author).like(f"%{query.lower()}%")) 
                ).all()           
        return render_template("adresult.html", book=book) 
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))

@app.route('/updatesec/<int:sec_id>', methods=['GET','POST'])
def updatesec(sec_id):
    dashboard = True
    if 'admin_id' in session:
        update_sec = Section.query.get(sec_id)
        if request.method == 'POST':
            name = request.form['name']
            desc = request.form['desc']

        
            if not name or not desc:
                flash('All fields are required.', 'error')
                return redirect(url_for('updatesec', sec_id = sec_id))
            
            update_sec.name = name
            update_sec.desc = desc
        
            db.session.commit()
            return redirect(url_for('admindashboard'))
        return render_template('updatesec.html', update_sec=update_sec, dashboard = dashboard)
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))
    
@app.route('/showbook/<int:book_id>', methods=['GET', 'POST'])
def showbook(book_id):
    if ('admin_id' in session):
        dashboard = True
        book = Books.query.filter_by(id = book_id).all()
        return render_template("bookcontent.html", dashboard = dashboard, book = book)    
    else:
        flash('Page access for Librarian only.', category='error')
        return redirect(url_for('login'))
    


@app.route('/admin_stats', methods=['GET', 'POST'])
def library_statistics():
    total_books = Books.query.count()
    books_issued = BookRequest.query.filter_by(approved=True).count()
    sections = Section.query.all()
    
    for section in sections:
        section.books_count = Books.query.filter_by(section=section).count()
        section.books_issued_count = BookRequest.query.filter(BookRequest.approved == True, BookRequest.books.has(section=section)).count()
    
    return render_template('adminstats.html', total_books=total_books, books_issued=books_issued, sections=sections)
