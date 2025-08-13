from flask import Flask, render_template, request, redirect, send_from_directory
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

db = SQLAlchemy(app)

# Model
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Create database
with app.app_context():
    db.create_all()
    print("✅ Database and tables created!")

@app.route('/')
def index():
    files = File.query.all()
    return render_template('index.html', files=files)

@app.route('/uploads', methods=['POST'])
def uploads():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        new_file = File(filename=filename)
        db.session.add(new_file)
        db.session.commit()
        print(f"✅ Saved {filename} to database.")
        return redirect('/')
    return 'Something went wrong, please try again.'

@app.route('/uploaded_file/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/download/<int:file_id>')
def download(file_id):
    file=File.query.get_or_404(file_id)
    return send_from_directory(app.config['UPLOAD_FOLDER'], file.filename, as_attachment=True)

@app.route('/delete/<int:file_id>')
def delete(file_id):
    file=File.query.get_or_404(file_id)
    filename=file.filename
    file_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
    os.remove(file_path)
    db.session.delete(file)
    db.session.commit()


    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
