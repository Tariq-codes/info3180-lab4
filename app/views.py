import os
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash, session, abort, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from werkzeug.utils import secure_filename
from app.models import UserProfile
from app.forms import LoginForm
from app.forms import UploadForm
from werkzeug.security import check_password_hash  



###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html', name="Mary Jane")


def get_uploaded_images():
    upload_folder = os.path.join(os.getcwd(), 'uploads')
    image_files = []
    
    if os.path.exists(upload_folder):
        for subdir, dirs, files in os.walk(upload_folder):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_files.append(file)  
    
    return image_files



@app.route('/uploads/<filename>')
def get_image(filename):
    upload_folder = os.path.abspath(os.path.join(os.getcwd(),'uploads')) 
    return send_from_directory(upload_folder, filename)


@app.route('/files')
@login_required
def files():
    images = get_uploaded_images()  # Get the list of uploaded images
    return render_template('files.html', images=images)



@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload():
    print("User is logged in:", current_user.is_authenticated)
    form = UploadForm()

    if form.validate_on_submit():
        file = form.file.data  # Get the uploaded file
        filename = secure_filename(file.filename)  
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)  

        file.save(file_path)

        flash('File uploaded successfully!', 'success')  
        return redirect(url_for('upload'))  
    return render_template('upload.html', form=form)



@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()

    # Validate 
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Query the database for the user
        user = db.session.execute(db.select(UserProfile).filter_by(username=username)).scalar()

        # Check if user exists and if password matches
        if user and user.check_password(password):
            login_user(user)  

            flash('Successfully logged in!', 'success')  # Flash success message
            return redirect(url_for("upload"))  # Redirect to upload form
        else:
            flash('Invalid username or password.', 'danger')  # Flash error message

    return render_template("login.html", form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()  
    flash('You have been logged out successfully.', 'info') 
    return redirect(url_for('home'))  


# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return db.session.execute(db.select(UserProfile).filter_by(id=id)).scalar()

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
), 'danger')

@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404
