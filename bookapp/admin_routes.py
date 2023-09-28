import random,os,string

from flask import render_template,request,abort,redirect,flash,make_response,session,url_for
from sqlalchemy.sql import text
#local imports
from bookapp import app,csrf
from bookapp.models import db,Admin,Book,Category
from bookapp import forms

def generate_string(howmany):
    x = random.sample(string.ascii_lowercase,howmany)
    return''.join(x)




@app.route("/admin/edit/book/<id>/",methods=["POST","GET"])
def edit_book(id):
    if session.get('adminuser')==None or session.get('role')!='admin':
        return redirect(url_for('admin_login'))
    else:
        if request.method=='GET':
            deets =db.session.query(Book).get_or_404(id)
            cats = db.session.query(Category).all()
            return render_template("/admin/editbook.html",deets=deets,cats=cats)
        else:
            book_2update = Book.query.get(id)

            book_2update.book_title = request.form.get('title')
            book_2update.cat_id = request.form.get('category')
            book_2update.book_status = request.form.get('status')
            book_2update.book_desc = request.form.get('description')
            book_2update.book_publication = request.form.get('yearpub')
            cover = request.files.get('cover')
            if cover.filename != '':
                name,ext =os.path.split(cover.filename)
                if ext.lower() in ['.jpg','.png','.jpeg']:
                    newfilename  = generate_string(10) + ext
                    cover.save('bookapp/static/uploads'+newfilename)
                    book_2update.book_cover = newfilename
                    flash('Your book has successfully been updated')
                    return redirect('/admin/books')
                else:
                    flash('the flash extension of the book wasnt included')
            db.session.commit()
            flash('Book detais was updated')
            return redirect(url_for('all_books'))


    


@app.route("/admin/delete/<id>/")
def book_delete(id):
    book = db.session.query(Book).get_or_404(id)
    filename = book.book_cover
    if filename != None and filename !='default.png' and os.path.isfile('bookapp/static/uploads/'+filename):
        os.remove('bookapp/static/uploads/'+filename)
    db.session.delete(book)
    db.session.commit()
    flash('book has been deleted')
    return redirect(url_for('all_books'))


@app.route('/admin/addbook', methods=['GET','POST'])
def addbook():
    if session.get('adminuser')==None or session.get('role') != 'admin':
        return redirect(url_for('admin_login')) 
    else:
        if request.method =='GET':
            cat=db.session.query(Category).all()
            return render_template('admin/addbook.html',cats=cat)
        else:
            #retrieve the file
            allowed=['jpg','png']
            filesobj=request.files['cover']
            filename=filesobj.filename
            newname='Default.png'
            #validation
            if filename=='':
                flash('Please Choose a book cover',category='error')
            else:                
                pieces=filename.split('.')
                ext=pieces[-1].lower()
                if ext in allowed:
                    newname=str(int(random.random()*10000000))+filename
                    filesobj.save('bookapp/static/uploads/'+ newname)
                else:
                    flash("Not Allowed, File Type Must Be ['jpg','png'], File was not uploades",category='error') 
                         
                     
            #retrieve all the form data
            title=request.form.get('title')
            category= request.form.get('category')
            status= request.form.get('status')
            description= request.form.get('description')
            yearpub= request.form.get('yearpub')
            cover=newname
            #insert to db
            bk=Book(book_title=title,book_desc=description,book_publication=yearpub,book_catid=category,book_status=status,book_cover=cover)
            db.session.add(bk)
            db.session.commit()
            if bk.book_id:
                flash('book has been added',category='info')
            else:
                flash("Please try again")

            return redirect(url_for('all_books'))

# @app.route('/admin/addbok',methods=["GET","POST"])
# def addbook():
#     if session.get("adminuser") == None or session.get('role')!= 'admin':#This means the Admin is not logged in
#         return redirect(url_for("admin_login"))
#     else:
#         if request.method=="GET":
#             cat =db.session.query(Category).all()
#             return render_template('admin/addbook.html',cat=cat)
#         else:
#             filesobj =request.files['cover']
#             filename =filesobj.filename
#             allowed =['jpg','png']
#             newname ='defalt.png'
#             if filename =='':
#                 flash("please chose a book cover",category='error')
#             else:
#                 newname = str(int(random.random()*1000000))+filename
#                 pieces = filename.split('.')
#                 ext =pieces[-1]
#                 if ext.lower() in allowed:
#                     filesobj.save("bookapp/static/uploads/"+filename)
#                 else:
#                     flash(f'Incorrect upload format : Alowed format = {allowed}')
#                     return redirect(url_for('all_books'))
                
#             title = request.form.get('title')
#             category = request.form.get('category')
#             status = request.form.get('status')
#             description = request.form.get('description')
#             yearpub = request.form.get('yearpub')
#             book =newname
#             bk = Book(book_title=title,book_desc=description,book_status=status,book_publication=yearpub,book_catid=category,book_cover=book)
#             db.session.add(bk)
#             db.session.commit()
#             if bk.book_id:
#                 flash('book hs been added ',category="bookerror")
#             else:
#                 flash('please try again',category='Notworking')
#         return redirect(url_for('all_books'))



            # return "Form has been submitted"



@app.route("/admin/books")
def all_books():
    if session.get("adminuser") == None or session.get('role')!= 'admin':#This means the Admin is not logged in
        return redirect(url_for("admin_login"))
    else:
        books = db.session.query(Book).all()
        return render_template("admin/allbooks.html",books=books)

@app.route("/admin/")
def admin_page():
    if session.get("adminuser") == None or session.get('role')!= 'admin':#This means the Admin is not logged in
        return render_template("admin/login.html")
    else:
        return redirect(url_for("admin_dashboard"))
    

@app.route("/admin/login/",methods=["GET","POST"])
def admin_login():
    if request.method=="GET":
        return render_template("admin/login.html")
    else:
        #collect the data from form
        username = request.form.get("username")
        pwd = request.form.get("pwd")
        
        #check if its in database
        check = db.session.query(Admin).filter(Admin.admin_username==username,Admin.admin_pwd==pwd).first()
        if check:
            session['adminuser']=check.admin_id
            session['role']='admin'
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid Login',category='error')
            return redirect(url_for('admin_login'))


@app.route("/admin/logout")
def admin_logout():
    if session.get('adminuser') !=None:# hes is still logged in
        session.pop('adminuser',None)
        session.pop('role',None)
        flash("You have been logged out ",category='info')
        return redirect(url_for('admin_login'))
    else:
        return redirect(url_for('admin_login'))

    

@app.route("/admin/dashboard")
def admin_dashboard():
    if session.get("adminuser") == None or session.get('role')!= 'admin':#This means the Admin is not logged in
        return redirect(url_for("admin_login"))
    else:
        return render_template('admin/dashboard.html')
    


@app.after_request
def after_request(response):
    response.headers["cache-control"]="no-cache, no-store, must-bookalidate"
    return response


