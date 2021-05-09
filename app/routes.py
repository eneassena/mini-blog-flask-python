from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditorProfile
from flask_login import current_user, login_user
from app.models import User
from flask_login import logout_user, login_required
from werkzeug.urls import url_parse
from datetime import datetime



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# rota de deslogar da conta
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for("index"))

# rota da page principal do site
@app.route("/")
@app.route("/index")
@login_required
def index():
	posts = [
		{
			'author': {'username': 'John'},
			'body': 'Beautiful day in Portland!'
		},
		{
			'author': {'username': 'Susan'},
			'body': 'The Avengers movie was so cool!'
		},
  		{
			'author': {'username': 'Elias Silva'},
			'body': 'Lorem ipsum dolor sit amet consectetur adipisicing elit. Provident, dicta.'
		}
	]
	return  render_template('index.html', title='Home Page', posts=posts)

# rota de cadastro de novos usuarios
@app.route("/register", methods=["GET", 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('index'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data,email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Cadastro realizado com êxito!')
		return redirect(url_for('login'))
	return render_template('register.html', title="Page Register", form=form)


# rota de login de usuarios
@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for("index"))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if (user is None) or (not user.check_password(form.password.data)):
			flash("data of acess is Invalid")
			return redirect(url_for("login"))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or url_parse(next_page).netloc != '':
			next_page = url_for('index')
		next_page = str(next_page).replace('/', '') 
		return redirect(url_for(next_page))
	return render_template('login.html', title="Sigin In", form=form)

# page de perfil de usuarios
@app.route("/user/<username>")
@login_required
def user(username):
	user = User.query.filter_by(username=username).first_or_404()
	posts = [
		{"author": user, 'body': "Test Post #1"},
		{"author": user, 'body': "Test Post #2"}
	]
	return render_template('user.html', user=user, posts=posts)
    
     
# rota de edição de profiles
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditorProfile()
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('edit_profile'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
		return render_template('edit_profile.html', title='Edit Profile', form=form)
	else:
		flash(f"Seu Texto tem tamanho de {len(form.about_me.data)} e passa do limite do campo about que permite 150 caracteres")
		return redirect(url_for('edit_profile'))

