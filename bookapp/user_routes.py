import random,string
import json,requests
from functools import wraps
from flask import render_template,request,abort,redirect,flash,make_response,session,url_for,request
from sqlalchemy.sql import text

from werkzeug.security import generate_password_hash, check_password_hash
#local imports
from bookapp import app,csrf,mail,Message
from bookapp.models import db,Book,User,Category,State,lga,Reviews,Contact,Donation
from bookapp.forms import* 






#this is a decorator used for validating all session
def login_required(f):
    @wraps(f)
    def login_check(*args,**kwargs):
        if session.get('userloggedin') !=None:
            return f(*args,**kwargs)
        else:
            flash('Access Denied')
            return redirect('/login')
    return login_check

def generate_string(howmany):#call this function as renerate_string(10)
    x = random.sample(string.digits,howmany)
    return ''.join(x)

@app.route('/landing')
@login_required
def landing():
    refno = session.get('trxno')
    transaction_deets = db.session.query(Donation).filter(Donation.don_refno==refno).first()
    #make a curl request to paystack end point 
    url="https://api.paystack.co/transaction/verify/"+transaction_deets.don_refno
    headers ={"Content_Type=":"application/json", "Authorization": "Bearer sk_test_9dbe896dcfd3742799aee38bb6d3df0278efe249"}
    response =  requests.get(url,headers=headers)
    rspjson = json.loads(response.text)
    if rspjson['status']== True:
        paystatus =rspjson['data']['gateway_response']
        transaction_deets.don_status ='Paid'
        db.session.commit()
        return redirect("/dashboard")
    else:
        flash("payment failed")
        return redirect('/reports')#dsiplay all the payment reports




@app.route('/intializ/paystack')
@login_required
def intialize_paystack():
    deets =User.query.get(session['userloggedin'])
    #make a curl rewuest to the pay
    refno = session.get('trxno')
    transaction_deets = db.session.query(Donation).filter(Donation.don_refno==refno).first()
    #make a curl request to paystack end point 
    url="https://api.paystack.co/transaction/initialize"
    headers ={"content_type=":"Content-Type: application/json", "Authorization": "Bearer sk_test_9dbe896dcfd3742799aee38bb6d3df0278efe249"}
    data={"email": deets.user_email,"amount": transaction_deets.don_amt,"reference":refno}
    response =  requests.post(url,headers=headers,data=json.dumps(data))
    rspjson =response.json()
    if rspjson['status']==True:
        redirectURL= rspjson['data']['authorization_url']
        return redirect(redirectURL)
    else:
        flash(" Please complete the form again")
        return redirect('/donate')
    # return rspjson
    # return rspjson
    


@app.route('/donation/', methods=['GET', 'POST'])
def donate():
    if request.method == 'GET':
        deets = db.session.query(User).get(session['userloggedin'])
        return render_template("user/donation_form.html", deets=deets)
    elif request.method == 'POST':
        amt = float(request.form.get('amount'))*100
        donor = request.form.get('fullname')
        email = request.form.get('email')
        # Generate a transaction reference for this transaction
        ref = "BW" + str(generate_string(8))
        # Insert into the database
        donation = Donation(don_amt=amt, don_userid=session['userloggedin'], don_email=email, don_fullname=donor, don_status='pending', don_refno=ref)
        db.session.add(donation)
        db.session.commit()
        # Save the reference no in session
        session['trxno'] = ref
        # Redirect to a confirmation page
        return redirect('/confirm_donation/')
    else:
        deets=db.session.query(User).get(session['userloggedin'])
        return render_template("user/donation_form.html",deets=deets)


@app.route('/confirm_donation/')
@login_required
def confirm_donation():
    deets= db.session.query(User).get(session['userloggedin'])
    if session.get('trxno')==None:
        flash('Please Complete this form', catergory='error')
        return redirect("/donate/")
    else:
        donation_deets=Donation.query.filter(Donation.don_refno==session['trxno']).first()
        return render_template("user/donation_confirmation.html",donation_deets=donation_deets,deets=deets)

@app.route('/sendmail')
def send_mail():
    msg = Message(subject="PAYMENT CONFIRMATION",sender='AUTOMOBILE',recipients=['jerilynnshafer342@gmail.com'],body="Thank you for contacting us")
    msg.html="""<h1 class='text-center'>Thank you Jeri Shafer Dluzansky for trusting us with your Automobile purchase.</h1>
                
                
             </div>
    """
    mail.send(msg)
    return 'done'


@app.route('/ajaxopt/',methods=['GET','POST'])
def ajax_options():
    cform = ContactForm()
    if request.method=='GET':
        return render_template('user/ajax_option.html',cform=cform)
    else:
        email =request.form.get('email')
        return f'thank you your email = {email} has been added'


@app.route('/review/<id>')
def review(id):
    books = db.session.query(Book).get_or_404(id)
    return render_template('user/reviews.html',books=books)


@app.route('/myreviews')
@login_required
def myreviews():
    id = session['userloggedin']
    userdeets =db.session.query(User).get(id)
    return render_template('user/myreviews.html',userdeets=userdeets)




@app.route('/submit_review/',methods=['POST'])
@login_required
def submit_review():
    title = request.form.get('title')
    content =request.form.get('content')
    userid =session['userloggedin']
    book = request.form.get('book')
    br = Reviews(rev_title=title,rev_text=content,rev_userid=userid,rev_bookid=book)
    db.session.add(br)
    db.session.commit()
    
    retstr =f"""<article class="blog-post">
      <h5 class="blog-post-title">{title }</h5>
      <p class="blog-post-meta"> Reviewed just now by <a href="#">{ br.reviewby.user_fullname}</a></p>

      <p>{content}</p>
      <hr> 
    </article>"""
    return retstr

@app.route('/dependent/')
def dependent_dropdown():

    states =db.session.query(State).all()
    return render_template('user/show_states.html',states=states)

@app.route('/lga/<stateid>')
def load_lgas(stateid):
    records =db.session.query(lga).filter(lga.state_id==stateid).all()
    str2return ="<select> class='from-control' name='lga' "
    for r in records:
        optstr = f"<option value='{r.lga_id}'>"+ r.lga_name +"</option>"
        str2return = str2return + optstr

    str2return = str2return+ '</select>'
    return str2return


@app.route('/contact')
def ajax_contact():
    data ="I am a srtring coming from the server"
    return render_template('user/ajax_test.html',data=data)

@app.route("/checkusername/")
def checkusername():
    email = request.args.get('email')
    deets = db.session.query(User).filter(User.user_email==email).first()
    if deets:
        return "your email is taken"
    else:
        return "invalid email"
    
    
    
   
    
    return 'not available'

@app.route("/submission/")
def ajax_submission():
    user = request.args.get("fullname")
    if user != "" and user != None:
        return f" Thank you {user} for completing the form"
    else:
        return " Please complete the form"
   


@app.route('/favourite')
def favourite_topics():
    bootcamp ={'name':'olusegun','topics':['html','css','python']}
    cats =db.session.query(Category).all()
    category=[c.cat_name for c in cats]
    
    return json.dumps(category)




@app.route('/profile', methods=['GET','POST'])
@login_required
def edit_profile():
    id = session.get('userloggedin')
    userdeets = db.session.query(User).get(id)
    pform = ProfileForm()
    if request.method =="GET":
        return render_template('user/editprofile.html',pform=pform,userdeets=userdeets)
    else:
        if pform.validate_on_submit:
            fullname = request.form.get('fullname')
            userdeets.user_fullname=fullname
            
            db.session.commit()
            flash('your profile has been updated')
            return redirect(url_for('dasboard'))
   

@app.route('/changedp',methods=['GET','POST'])
@login_required
def changedp():
    dpform = DpForm()
    id = session.get('userloggedin')
    userdeets =db.session.query(User).get(id)
    if request.method =="GET":
        return render_template('user/changedp.html',dpform=dpform,userdeets=userdeets)
    else:
        if dpform.validate_on_submit():
            pix =request.files.get('dp')
            filename =pix.filename
            pix.save(app.config['USER_PROFILE_PATH']+filename)
            userdeets.user_pix =filename
            db.session.commit()
            flash("Profile poicture has been uodated",category="info")
            return redirect(url_for('dasboard'))
        else:
            return render_template('user/changedp.html',dpform=dpform,userdeets=userdeets)
    
    

@app.route('/viewall/')
@login_required
def viewall():
    books = db.session.query(Book).filter(Book.book_status=='1').all()
    cat= db.session.query(Category).all()
    return render_template('user/viewall.html',books=books,cat=cat)


@app.route('/logout')
def logout():
    if session.get('userloggedin')!=None:
        session.pop('userloggedin',None)
    return redirect('/')

@app.route('/dashboard')
def dasboard():
    if session.get("userloggedin") != None:
        id = session.get("userloggedin")
        userdeets= User.query.get(id)
        return render_template('user/dashboard.html',userdeets=userdeets)
    else:
        flash("You Need To login to access this page")
        return redirect('/login')



@app.route('/login',methods=['POST','GET'])
def login():
    if request.method =="GET":
        return render_template('user/loginpage.html')
    else:
        email = request.form.get('email')
        pwd =request.form.get('pwd')
        deets = db.session.query(User).filter(User.user_email==email).first()
        if deets != None:
            hashed_pwd =deets.user_pwd

            if check_password_hash(hashed_pwd,pwd)==True:
                session['userloggedin']=deets.user_id

                return redirect('/dashboard')
            else:
                flash('invalid credentials, try again')
                return redirect('/login')
        else:
            flash('invalid Credentials, try again')
            return redirect('/login')





@app.route('/register',methods=['POST','GET'])
def register():
    regform = RegForm()
    if request.method =='GET':
        return render_template('user/signup.html',regform=regform)
    else:
        if regform.validate_on_submit():
            fullname = request.form.get('fullname')
            email = request.form.get('email')
            pwd = request.form.get('pwd')
            hashed_pwd = generate_password_hash(pwd)
            user=User(user_fullname=fullname,user_email=email,user_pwd=hashed_pwd,)
            db.session.add(user)
            db.session.commit()
            flash('An account has been created for you')
            return redirect('/login')
        else:
            return render_template('user/signup.html',regform=regform)
        


@app.route('/book/details/<id>')
def book_details(id):
    books = db.session.query(Book).get_or_404(id)
    return render_template('user/reviews.html',books=books)



# home page
@app.route("/")
def home_page():
    books = db.session.query(Book).filter(Book.book_status == '1').limit(4).all()
    # connect to the endpoint http:127.0.0.1:1995/api/v1.0/listall to collect data of book
    # pas it to th templates and display on the template
   
    # response = requests.get('http://127.0.0.1:5000/api/v1.0/listall/')
    #     # import requests
    # rsp = json.loads(response.text)#response.json
    
        # rsp = None #if the server is unreacheable...
    return render_template("user/home_page.html",books=books)


