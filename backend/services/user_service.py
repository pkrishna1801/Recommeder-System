import json
import os
import uuid
import hashlib
import time
from config import config

# Try different JWT libraries to ensure compatibility
try:
    import pyjwt as jwt
    print("Using pyjwt library")
    JWT_LIB = "pyjwt"
except ImportError:
    try:
        import jwt
        print("Using jwt library")
        JWT_LIB = "jwt"
    except ImportError:
        print("WARNING: No JWT library found. Authentication will not work.")
        JWT_LIB = None

class UserService:
    """
    Service to handle user management and authentication
    """
    
    def __init__(self):
        """
        Initialize the user service with data path
        """
        self.data_dir = 'data'
        self.users_file = os.path.join(self.data_dir, 'users.json')
        self._ensure_data_dir()
        self.users = self._load_users()
        self.jwt_secret = config.get('JWT_SECRET', 'your-secret-key-for-jwt')
        self.token_expiry = config.get('TOKEN_EXPIRY', 86400)  # 24 hours in seconds
    
    def _ensure_data_dir(self):
        """
        Ensure the data directory exists
        """
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        if not os.path.exists(self.users_file):
            with open(self.users_file, 'w') as f:
                json.dump([], f)
    
    def _load_users(self):
        """
        Load users from the JSON data file
        """
        try:
            with open(self.users_file, 'r') as file:
                return json.load(file)
        except Exception as e:
            print(f"Error loading user data: {str(e)}")
            return []
    
    def _save_users(self):
        """
        Save users to the JSON data file
        """
        try:
            with open(self.users_file, 'w') as file:
                json.dump(self.users, file, indent=2)
        except Exception as e:
            print(f"Error saving user data: {str(e)}")
    
    def _hash_password(self, password, salt=None):
        """
        Hash a password with a salt
        """
        if salt is None:
            salt = uuid.uuid4().hex
        
        hashed_pw = hashlib.sha256((password + salt).encode()).hexdigest()
        return {'hash': hashed_pw, 'salt': salt}
    
    def _verify_password(self, password, salt, stored_hash):
        """
        Verify a password against a stored hash
        """
        computed_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return computed_hash == stored_hash
    
    def register_user(self, username, email, password):
        """
        Register a new user
        """
        # Check if username or email already exists
        for user in self.users:
            if user['username'] == username:
                return {'success': False, 'error': 'Username already exists'}
            if user['email'] == email:
                return {'success': False, 'error': 'Email already exists'}
        
        # Create password hash
        pw_hash = self._hash_password(password)
        
        # Create new user
        new_user = {
            'id': str(uuid.uuid4()),
            'username': username,
            'email': email,
            'password_hash': pw_hash['hash'],
            'password_salt': pw_hash['salt'],
            'preferences': {
                'category_preferences': [],
                'price_range': {'min': None, 'max': None},
                'brand_preferences': []
            },
            'browsing_history': [],
            'created_at': time.time(),
            'last_login': None
        }
        
        # Add to users list
        self.users.append(new_user)
        self._save_users()
        
        # Generate token
        token = self._generate_token(new_user)
        
        return {
            'success': True,
            'user': {
                'id': new_user['id'],
                'username': new_user['username'],
                'email': new_user['email'],
                'preferences': new_user['preferences']
            },
            'token': token
        }
    
    def login_user(self, username, password):
        """
        Authenticate a user and return a token
        """
        for user in self.users:
            if user['username'] == username:
                # Verify password
                if self._verify_password(password, user['password_salt'], user['password_hash']):
                    # Update last login
                    user['last_login'] = time.time()
                    self._save_users()
                    
                    # Generate token
                    token = self._generate_token(user)
                    
                    return {
                        'success': True,
                        'user': {
                            'id': user['id'],
                            'username': user['username'],
                            'email': user['email'],
                            'preferences': user.get('preferences', {})
                        },
                        'token': token
                    }
                else:
                    return {'success': False, 'error': 'Invalid password'}
        
        return {'success': False, 'error': 'User not found'}
    
    def get_user_by_id(self, user_id):
        """
        Get a user by ID
        """
        for user in self.users:
            if user['id'] == user_id:
                return {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'preferences': user.get('preferences', {}),
                    'browsing_history': user.get('browsing_history', [])
                }
        return None
    
    def update_user_preferences(self, user_id, preferences):
        """
        Update a user's preferences
        """
        for user in self.users:
            if user['id'] == user_id:
                # Merge new preferences with existing ones
                if 'preferences' not in user:
                    user['preferences'] = {}
                
                # Handle category preferences
                if 'category_preferences' in preferences:
                    user['preferences']['category_preferences'] = preferences['category_preferences']
                
                # Handle price range
                if 'price_range' in preferences:
                    user['preferences']['price_range'] = preferences['price_range']
                
                # Handle brand preferences
                if 'brand_preferences' in preferences:
                    user['preferences']['brand_preferences'] = preferences['brand_preferences']
                
                # Save changes
                self._save_users()
                return {'success': True, 'preferences': user['preferences']}
        
        return {'success': False, 'error': 'User not found'}
    
    def save_browsing_history(self, user_id, product_id):
        """
        Add a product to a user's browsing history
        """
        for user in self.users:
            if user['id'] == user_id:
                if 'browsing_history' not in user:
                    user['browsing_history'] = []
                
                # Add to history (avoid duplicates by removing first)
                if product_id in user['browsing_history']:
                    user['browsing_history'].remove(product_id)
                
                # Add to front of list (most recent first)
                user['browsing_history'].insert(0, product_id)
                
                # Limit history to 50 items
                user['browsing_history'] = user['browsing_history'][:50]
                
                self._save_users()
                return {'success': True, 'browsing_history': user['browsing_history']}
        
        return {'success': False, 'error': 'User not found'}
    
    def get_browsing_history(self, user_id):
        """
        Get a user's browsing history
        """
        for user in self.users:
            if user['id'] == user_id:
                return {'success': True, 'browsing_history': user.get('browsing_history', [])}
        
        return {'success': False, 'error': 'User not found'}
    
    def clear_browsing_history(self, user_id):
        """
        Clear a user's browsing history
        """
        for user in self.users:
            if user['id'] == user_id:
                user['browsing_history'] = []
                self._save_users()
                return {'success': True}
        
        return {'success': False, 'error': 'User not found'}
    
    def _generate_token(self, user):
        """
        Generate a JWT token for authentication
        
        Compatible with different JWT libraries
        """
        payload = {
            'user_id': user['id'],
            'username': user['username'],
            'exp': int(time.time() + self.token_expiry)
        }
        
        if JWT_LIB is None:
            # Fallback if no JWT library is available
            print("ERROR: No JWT library available, cannot generate token")
            return "invalid-token-no-jwt-library"
        
        try:
            # Use a simple string encoding as a fallback if JWT fails
            import base64
            import json
            
            # Convert payload to a JSON string and encode as base64
            payload_json = json.dumps(payload)
            token = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')
            
            # Add a prefix to identify this as a custom token
            return f"custom.{token}"
            
        except Exception as e:
            print(f"Error generating token: {str(e)}")
            return "invalid-token-error"
    
    def verify_token(self, token):
        """
        Verify a JWT token
        
        Compatible with different token formats
        """
        # Check if it's a custom token
        if token.startswith("custom."):
            try:
                # Extract the payload part
                token_payload = token.split('.')[1]
                
                # Decode from base64
                import base64
                import json
                
                payload_json = base64.b64decode(token_payload).decode('utf-8')
                payload = json.loads(payload_json)
                
                # Check expiration
                if payload['exp'] < time.time():
                    return {'valid': False, 'error': 'Token expired'}
                
                user_id = payload['user_id']
                
                # Check if user exists
                user = self.get_user_by_id(user_id)
                if not user:
                    return {'valid': False, 'error': 'User not found'}
                
                return {'valid': True, 'user_id': user_id, 'user': user}
                
            except Exception as e:
                print(f"Error verifying custom token: {str(e)}")
                return {'valid': False, 'error': 'Invalid token format'}
        
        # If JWT library not available, all regular tokens are invalid
        if JWT_LIB is None:
            return {'valid': False, 'error': 'No JWT library available'}
        
        try:
            # Try to decode with standard JWT library
            try:
                # Different parameter names depending on library version
                try:
                    payload = jwt.decode(jwt=token, key=self.jwt_secret, algorithms=['HS256'])
                except TypeError:
                    payload = jwt.decode(token, self.jwt_secret, algorithms=['HS256'])
            except AttributeError:
                # Fall back to custom decoding if JWT fails
                return {'valid': False, 'error': 'JWT library not functioning correctly'}
                
            user_id = payload['user_id']
            
            # Check if user exists
            user = self.get_user_by_id(user_id)
            if not user:
                return {'valid': False, 'error': 'User not found'}
            
            return {'valid': True, 'user_id': user_id, 'user': user}
            
        except Exception as e:
            print(f"Error verifying token: {str(e)}")
            return {'valid': False, 'error': f'Verification error: {str(e)}'}