from flask import Blueprint, request, jsonify
from src.models.user import db, User
import jwt
from datetime import datetime, timedelta
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Chave secreta para JWT (em produção, use uma variável de ambiente)
JWT_SECRET = 'treino-app-secret-key-2024'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'message': 'Token é obrigatório'}), 401
        
        try:
            # Remove 'Bearer ' do token se presente
            if token.startswith('Bearer '):
                token = token[7:]
            
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user = User.query.get(data['user_id'])
            
            if not current_user:
                return jsonify({'message': 'Token inválido'}), 401
                
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'Token expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401
        
        return f(current_user, *args, **kwargs)
    
    return decorated

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validação básica
        if not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'message': 'Username, email e password são obrigatórios'}), 400
        
        # Verificar se usuário já existe
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'message': 'Username já existe'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'message': 'Email já existe'}), 400
        
        # Criar novo usuário
        user = User(
            username=data['username'],
            email=data['email'],
            name=data.get('name', ''),
            age=data.get('age'),
            gender=data.get('gender', ''),
            height=data.get('height'),
            weight=data.get('weight'),
            experience=data.get('experience', ''),
            frequency=data.get('frequency', ''),
            duration=data.get('duration', ''),
            goal=data.get('goal', '')
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        # Gerar token JWT
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'token': token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data.get('username') or not data.get('password'):
            return jsonify({'message': 'Username e password são obrigatórios'}), 400
        
        # Buscar usuário
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'message': 'Credenciais inválidas'}), 401
        
        # Gerar token JWT
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=30)
        }, JWT_SECRET, algorithm='HS256')
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'token': token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile(current_user):
    return jsonify({'user': current_user.to_dict()}), 200

@auth_bp.route('/profile', methods=['PUT'])
@token_required
def update_profile(current_user):
    try:
        data = request.get_json()
        
        # Atualizar campos do perfil
        if 'name' in data:
            current_user.name = data['name']
        if 'age' in data:
            current_user.age = data['age']
        if 'gender' in data:
            current_user.gender = data['gender']
        if 'height' in data:
            current_user.height = data['height']
        if 'weight' in data:
            current_user.weight = data['weight']
        if 'experience' in data:
            current_user.experience = data['experience']
        if 'frequency' in data:
            current_user.frequency = data['frequency']
        if 'duration' in data:
            current_user.duration = data['duration']
        if 'goal' in data:
            current_user.goal = data['goal']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Perfil atualizado com sucesso',
            'user': current_user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@auth_bp.route('/verify-token', methods=['POST'])
@token_required
def verify_token(current_user):
    return jsonify({
        'valid': True,
        'user': current_user.to_dict()
    }), 200

