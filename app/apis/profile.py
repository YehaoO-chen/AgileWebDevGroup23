

from flask import jsonify, request, url_for
from flask_login import current_user, login_required
from sqlite3 import IntegrityError
from werkzeug.utils import secure_filename
from app.models import User
from app import db
from PIL import Image
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_api_profile(app):
    # Define the upload folder relative to the app's root path
    # Ensure the UPLOAD_FOLDER exists
    UPLOAD_FOLDER = os.path.join(app.root_path,'static', 'uploads')
    if not os.path.exists(UPLOAD_FOLDER):
        try:
            os.makedirs(UPLOAD_FOLDER) # Create the directory if it doesn't exist
            print(f"Created directory: {UPLOAD_FOLDER}")
        except OSError as e:
            print(f"Error creating directory {UPLOAD_FOLDER}: {e}")
            # Handle the error appropriately, maybe raise it or log critical error

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER # Store in app config
    app.config['MAX_IMAGE_SIZE'] = 256 # Define max size for resizing
    
    
    @app.route('/api/profile', methods=['GET'])
    @login_required
    def get_profile():
        user = current_user
        return jsonify({
            'id': user.id,
            'username': user.username,
            'create_time': user.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'fullname': user.fullname,
            'major': user.major,
            'email': user.email,
            'phone': user.phone,
            'address': user.address,
            'student_id': user.student_id,
            'avatar': user.avatar
        })


    @app.route('/api/profile', methods=['PUT'])
    @login_required
    def update_profile():
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'Invalid input data'}), 400

        user = current_user
        errors = {}

        # --- Update fields and perform checks ---

        # Username (check uniqueness if changed)
        new_username = data.get('username')
        if new_username and new_username != user.username:
            existing_user = User.query.filter(User.username == new_username, User.id != user.id).first()
            if existing_user:
                errors['username'] = 'Username already taken.'
            else:
                user.username = new_username

        # Email (check uniqueness if changed)
        new_email = data.get('email')
        if new_email and new_email != user.email:
            existing_user = User.query.filter(User.email == new_email, User.id != user.id).first()
            if existing_user:
                errors['email'] = 'Email already registered.'
            else:
                user.email = new_email
        elif 'email' in data and not new_email: # Allow setting email to null if desired and model allows
                user.email = None


        # Phone (check uniqueness if changed)
        new_phone = data.get('phone')
        if new_phone and new_phone != user.phone:
            existing_user = User.query.filter(User.phone == new_phone, User.id != user.id).first()
            if existing_user:
                errors['phone'] = 'Phone number already registered.'
            else:
                user.phone = new_phone
        elif 'phone' in data and not new_phone: # Allow setting phone to null
            user.phone = None

        # Student ID (check uniqueness if changed)
        new_student_id = data.get('student_id')
        if new_student_id and new_student_id != user.student_id:
            existing_user = User.query.filter(User.student_id == new_student_id, User.id != user.id).first()
            if existing_user:
                errors['student_id'] = 'Student ID already registered.'
            else:
                user.student_id = new_student_id
        elif 'student_id' in data and not new_student_id: # Allow setting student_id to null
            user.student_id = None

        # Update other nullable fields directly if provided
        if 'fullname' in data:
            user.fullname = data.get('fullname')
        if 'major' in data:
            user.major = data.get('major')
        if 'address' in data:
            user.address = data.get('address')

        # --- Commit changes if no errors ---
        if errors:
            return jsonify({'success': False, 'errors': errors}), 400

        try:
            db.session.commit()
            return jsonify({'success': True, 'message': 'Profile updated successfully.'})
        except IntegrityError as e:
            db.session.rollback()
            # This might catch uniqueness errors missed above, though less specific
            return jsonify({'success': False, 'error': 'Database error: Could not update profile. Check unique fields.'}), 500
        except Exception as e:
            db.session.rollback()
            # Log the exception e for debugging
            print(f"Error updating profile: {e}")
            return jsonify({'success': False, 'error': 'An unexpected error occurred.'}), 500



    @app.route('/api/upload_avatar', methods=['POST'])
    @login_required
    def upload_avatar():
        # Check if the post request has the file part
        if 'avatar' not in request.files:
            return jsonify({'success': False, 'error': 'No file part in the request'}), 400
        
        file = request.files['avatar']
        
        # If the user does not select a file, the browser submits an empty file without a filename.
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No selected file'}), 400
        
        if file and allowed_file(file.filename):
            # Generate a secure filename and add user-specific prefix to avoid collisions
            original_extension = file.filename.rsplit('.', 1)[1].lower()
            # Using user ID is safer than username for uniqueness and avoiding special chars
            filename = secure_filename(f"user_{current_user.id}_avatar.{original_extension}")
            save_path = os.path.join( app.config['UPLOAD_FOLDER'] , filename)
            
            try:
                # --- Optional: Delete old avatar file before saving new one ---
                if current_user.avatar and current_user.avatar != 'default.jpg':
                    old_avatar_path = os.path.join(app.config['UPLOAD_FOLDER'], current_user.avatar)
                    if os.path.exists(old_avatar_path):
                        try:
                            os.remove(old_avatar_path)
                        except OSError as e:
                            print(f"Error deleting old avatar {old_avatar_path}: {e}") # Log error but continue
                
                # --- End Optional ---

                # --- Image Resizing Logic ---
                max_size = app.config['MAX_IMAGE_SIZE']
                img = Image.open(file.stream) # Open image from the file stream
                width, height = img.size
                resized = False

                if max(width, height) > max_size:
                    ratio = max_size / max(width, height)
                    new_width = int(width * ratio)
                    new_height = int(height * ratio)
                    # Use LANCZOS for high-quality downsampling
                    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                    resized = True
                    print(f"Resized image to: {new_width}x{new_height}") # Optional logging

                # Handle image format and transparency for saving
                save_format = original_extension.upper()
                if save_format == 'JPG':
                    save_format = 'JPEG' # Pillow uses 'JPEG'

                # If saving as JPEG and image has alpha channel (transparency), convert to RGB
                if save_format == 'JPEG' and img.mode in ('RGBA', 'P'):
                        img = img.convert('RGB')

                # Save the (potentially resized) image
                img.save(save_path, format=save_format, quality=85, optimize=True) # Adjust quality as needed
                # --- End Image Resizing Logic ---
                
                # Update user avatar field in the database with the new filename
                current_user.avatar = filename
                db.session.commit()
                
                # Construct the URL path for the frontend
                # Assumes 'static' is served at the root URL path '/static'
                avatar_url = url_for('static', filename=f'uploads/{filename}', _external=False) # Use relative URL

                return jsonify({'success': True, 'avatar_url': avatar_url, 'filename': filename})

            except IntegrityError as e:
                    db.session.rollback()
                    return jsonify({'success': False, 'error': 'Database error saving avatar reference.'}), 500
            except Exception as e:
                db.session.rollback() # Rollback DB changes if file save fails after potential DB update attempt
                print(f"Error saving avatar: {e}") # Log the error
                return jsonify({'success': False, 'error': f'Failed to save file: {str(e)}'}), 500
        else:
            return jsonify({'success': False, 'error': 'File type not allowed'}), 400


    @app.route('/api/users', methods=['GET'])
    @login_required
    def get_users():
        try:
            # Get all users except the current user
            users = User.query.filter(User.id != current_user.id).all()
            print(f"Found {len(users)} users for sharing")
            
            result = [{
                'id': user.id,
                'username': user.username
            } for user in users]
            
            return jsonify(result)
        except Exception as e:
            print(f"Error getting users: {str(e)}")
            return jsonify([]), 500

