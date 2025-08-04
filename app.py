from flask import Flask, render_template, request, redirect, url_for,flash,session, send_from_directory
from models import db, Student,Job, Application, Category, Tag
from datetime import datetime
from flask_migrate import Migrate

import os
from werkzeug.utils import secure_filename
from forms import LoginForm, RegistrationForm, JobPostForm, ApplicationStatusUpdateForm, TagForm, CategoryForm

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///branchlogic.db'
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = './static/resumes'  # Folder to save uploaded resumes

db.init_app(app)
migrate = Migrate(app, db)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check if the user is an admin (fixed credentials)
        if username == 'manii1346' and password == '1346':  
            session['user_id'] = 'admin'  
            session['user_type'] = 'admin'  # These two lines check whether the enterd user is admin or not
            flash('Welcome back Admin')
            return redirect(url_for('admin_dashboard'))

        # Check if student is logging in
        student = Student.query.filter_by(username=username, password=password).first()
        if student:
            session['user_id'] = student.student_id
            session['user_type'] = 'student'
            flash(f'Welcome Student {student.name}!', 'success')
            return redirect(url_for('student_dashboard', student_id=student.student_id))

        flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        name = form.name.data
        password = form.password.data
        resume_file = request.files.get('resume')

        resume_path = None
        if resume_file:
            resume_path = f"{app.config['UPLOAD_FOLDER']}/{resume_file.filename}"
            resume_file.save(resume_path)

        new_student = Student(
            username=username,
            email=email,
            name=name,
            password=password,
            resume=resume_path
        )
        db.session.add(new_student)
        db.session.commit()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template("register.html", form=form)


# admin functionalities

@app.route('/admin/dashboard')
def admin_dashboard():
    total_students = Student.query.count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()

    jobs = Job.query.all()
    visible_jobs = Job.query.filter_by(is_visible=True).all()

    applications = Application.query.all()

    return render_template(
        'admin/admin_dashboard.html',
        total_students=total_students,
        total_jobs=total_jobs,
        total_applications=total_applications,
        jobs=jobs,
        applications=applications
    )

# -------------------------------------------
# 📋 View Applicants for a Job (Admin)
# -------------------------------------------
@app.route('/admin/job/<int:job_id>/applicants')
def view_applicants(job_id):
    job = Job.query.get_or_404(job_id)
    applications = Application.query.filter_by(job_id=job_id).all()
    return render_template('admin/view_applicants.html', job=job, applications=applications)

# -------------------------------------------
# 📝 Update Application Status
# -------------------------------------------
@app.route('/application/<int:application_id>/update', methods=['GET', 'POST'])
def update_application(application_id):
    application = Application.query.get_or_404(application_id)
    form = ApplicationStatusUpdateForm()

    if form.validate_on_submit():
        application.status = form.status.data
        application.remarks = form.remarks.data
        db.session.commit()
        flash('Application status updated.', 'success')
        return redirect(url_for('view_applicants', job_id=application.job_id))

    return render_template('admin/update_application.html', form=form, application=application)

# -------------------------------------------
# 📈 Admin Dashboard Stats & Analytics
# -------------------------------------------
@app.route('/admin/analytics')
def admin_analytics():
    total_students = Student.query.count()
    total_jobs = Job.query.count()
    total_applications = Application.query.count()
    return render_template('admin/analytics.html', total_students=total_students, total_jobs=total_jobs, total_applications=total_applications)

# -------------------------------------------
# 🔍 Search & Filter Candidates (Admin)
# -------------------------------------------
@app.route('/admin/search_candidates')
def search_candidates():
    query = request.args.get('q', '')
    students = Student.query.filter(
        (Student.skills.ilike(f"%{query}%")) |
        (Student.qualification.ilike(f"%{query}%"))
    ).all()
    return render_template('admin/search_candidates.html', students=students, query=query)

# -------------------------------------------
# 📁 Category Management (Admin)
# -------------------------------------------
@app.route('/admin/categories', methods=['GET', 'POST'])
def manage_categories():
    form = CategoryForm()
    if form.validate_on_submit():
        category = Category(name=form.name.data)
        db.session.add(category)
        db.session.commit()
        flash('Category added!', 'success')
    categories = Category.query.all()
    return render_template('admin/categories.html', form=form, categories=categories)

# -------------------------------------------
# 🏷️ Tag Management (Admin)
# -------------------------------------------
@app.route('/admin/tags', methods=['GET', 'POST'])
def manage_tags():
    form = TagForm()
    if form.validate_on_submit():
        tag = Tag(name=form.name.data)
        db.session.add(tag)
        db.session.commit()
        flash('Tag added!', 'success')
    tags = Tag.query.all()
    return render_template('admin/tags.html', form=form, tags=tags)

# -------------------------------------------
# ✏️ Edit Job Posting
# -------------------------------------------
@app.route('/admin/job/<int:job_id>/edit', methods=['GET', 'POST'])
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    form = JobPostForm(obj=job)
    if form.validate_on_submit():
        form.populate_obj(job)
        db.session.commit()
        flash('Job updated!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/job_form.html', form=form)

# -------------------------------------------
# ❌ Delete Job
# -------------------------------------------
@app.route('/admin/job/<int:job_id>/delete', methods=['POST'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('Job deleted!', 'info')
    return redirect(url_for('admin_dashboard'))

# -------------------------------------------
# 👁️ Toggle Job Visibility
# -------------------------------------------
@app.route('/admin/job/<int:job_id>/toggle_visibility')
def toggle_job_visibility(job_id):
    job = Job.query.get_or_404(job_id)
    job.is_visible = not job.is_visible
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

# -------------------------------------------
# ➕ Create New Job
# -------------------------------------------
@app.route('/admin/job/new', methods=['GET', 'POST'])
def create_job():
    form = JobPostForm()
    if form.validate_on_submit():
        deadline_str = request.form.get('deadline')  # or use form.deadline.data if using WTForms DateField
        try:
            deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
        except ValueError:
            flash('Invalid deadline format. Please use YYYY-MM-DD.', 'danger')
            return redirect(request.url)

        job = Job(
            title=form.title.data,
            description=form.description.data,
            skills_required=form.skills_required.data,
            salary_range=form.salary_range.data,
            location=form.location.data,
            deadline=deadline,
            is_visible=True,
            posted_at=datetime.utcnow()
        )
        db.session.add(job)
        db.session.commit()
        flash('Job posted successfully!', 'success')
        return redirect(url_for('admin_dashboard'))
    return render_template('admin/job_form.html', form=form)



# -----------------------------------------------
# 📄 Admin - View Resume Database (All Students)
# -----------------------------------------------
@app.route('/admin/resumes')
def resume_database():
    students = Student.query.all()
    return render_template('admin/resume_database.html', students=students)

# -----------------------------------------------
# 🧑‍🎓 Student Dashboard
# -----------------------------------------------
@app.route('/student_dashboard/<int:student_id>')
def student_dashboard(student_id):
    student = Student.query.get_or_404(student_id)
    jobs = Job.query.all()
    recent_applications = Application.query.filter_by(student_id=student_id).order_by(Application.applied_at.desc()).limit(5).all()
    return render_template('student/student_dashboard.html', student=student, jobs=jobs, recent_applications=recent_applications)



# -----------------------------------------------
# 📝 Apply for a Job (Student)
# -----------------------------------------------
@app.route('/apply/<int:job_id>/<int:student_id>', methods=['POST'])
def apply_job(job_id, student_id):
    # Check if already applied
    existing_application = Application.query.filter_by(student_id=student_id, job_id=job_id).first()
    if existing_application:
        flash("You have already applied for this job.", "info")
        return redirect(url_for('student_dashboard', student_id=student_id))

    # Create new application
    application = Application(
        student_id=student_id,
        job_id=job_id,
        applied_at=datetime.utcnow(),
        status='pending'
    )
    db.session.add(application)
    db.session.commit()

    flash("Application submitted successfully!", "success")
    return redirect(url_for('student_dashboard', student_id=student_id))




# -----------------------------------------------
# 📋 View Student's Applications
# -----------------------------------------------
@app.route('/student/<int:student_id>/applications')
def student_applications(student_id):
    student = Student.query.get_or_404(student_id)
    applications = Application.query.filter_by(student_id=student_id).all()
    return render_template('student/student_applications.html', student=student, applications=applications)


# -----------------------------------------------
# 🔍 Student Search for Jobs
# -----------------------------------------------
@app.route('/student/<int:student_id>/search')
def student_search(student_id):
    query = request.args.get('q', '')
    jobs = Job.query.filter(Job.title.ilike(f"%{query}%"), Job.is_visible == True).all()
    return render_template('student/search_results.html', jobs=jobs, query=query, student_id=student_id)


# -----------------------------------------------
# 📥 Download Resume (Admin or Self)
# -----------------------------------------------
@app.route('/download_resume/<filename>')
def download_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

# -----------------------------------------------
# 📄 View Job Detail (as Student)
# -----------------------------------------------
@app.route('/student/<int:student_id>/job/<int:job_id>')
def student_job_detail(student_id, job_id):
    job = Job.query.get_or_404(job_id)
    return render_template('student/job_detail.html', job=job, student_id=student_id)
@app.route('/update_profile', methods=['POST'])
def update_profile():
    student_id = session.get('student_id')
    student = Student.query.get(student_id)

    student.name = request.form['name']
    student.email = request.form['email']

    if 'resume' in request.files:
        resume_file = request.files['resume']
        if resume_file.filename:
            resume_filename = secure_filename(resume_file.filename)
            resume_path = os.path.join(app.config['UPLOAD_FOLDER'], resume_filename)
            resume_file.save(resume_path)
            student.resume = resume_filename

    db.session.commit()
    flash("Profile updated successfully", "success")
    return redirect(url_for('student_dashboard'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)    
    session.pop('user_type', None)  
    flash('Logged out successfully!')
    return redirect(url_for('login'))   

if __name__ == '__main__':
    with app.app_context():
       db.create_all()

    app.run(host='0.0.0.0',debug=True)


