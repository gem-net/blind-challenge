from datetime import datetime

from flask import redirect, url_for, render_template, flash, abort, g, send_file
from flask_login import login_required, login_user, logout_user

from . import app, update_drive_listing
from .forms import LoginForm
from .models import User


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User()
        if not user.check_password(form.password.data):
            flash('Incorrect password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('review'))
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/reload')
def load_members_list():
    if True:
        update_drive_listing()
        flash('File listing updated.', 'message')
        return render_template('reload.html')
    else:
        abort(404)


@app.route('/')
@login_required
def review():
    if True:
        return render_template("review.html", df=g.review.df, cols_show=g.review.cols_show)
    else:
        abort(404)


@app.route('/download/<file_id>')
def download(file_id):
    from .review import download_file

    files = g.review.df
    try:
        file_info = files[files.id == file_id].iloc[0]
    except IndexError:
        flash('File not found', 'error')
        return redirect(url_for('download'))
    title = file_info.title
    mime_orig = file_info.mimeType
    fh, filename, mime_out = download_file(file_id, title=title, mime_orig=mime_orig)
    fh.seek(0)
    return send_file(fh, mimetype=mime_out,
                     as_attachment=True, attachment_filename=filename)


@app.route('/build_zip')
def get_folder_zip():
    from .review import download_folder_zip

    files = g.review.df
    zipped_file = download_folder_zip(files)
    time_str = datetime.utcnow().strftime('%Y-%m-%d_%H:%M:%SZ')
    out_name = 'C-GEM_files_{}.zip'.format(time_str)
    zipped_file.seek(0)
    return send_file(zipped_file, mimetype='application/zip',
                     as_attachment=True, attachment_filename=out_name)
