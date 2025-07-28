from flask import Blueprint, request, jsonify
from src.models.user import db, WorkoutHistory
from src.routes.auth import token_required
from datetime import datetime

workout_bp = Blueprint('workout', __name__)

@workout_bp.route('/history', methods=['GET'])
@token_required
def get_workout_history(current_user):
    try:
        # Buscar histórico de treinos do usuário
        history = WorkoutHistory.query.filter_by(user_id=current_user.id)\
                                    .order_by(WorkoutHistory.created_at.desc())\
                                    .all()
        
        return jsonify({
            'history': [workout.to_dict() for workout in history]
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@workout_bp.route('/history', methods=['POST'])
@token_required
def save_workout(current_user):
    try:
        data = request.get_json()
        
        # Validação básica
        if not data.get('workout_id') or not data.get('workout_name') or not data.get('exercises'):
            return jsonify({'message': 'workout_id, workout_name e exercises são obrigatórios'}), 400
        
        # Criar novo registro de treino
        workout = WorkoutHistory(
            user_id=current_user.id,
            workout_id=data['workout_id'],
            workout_name=data['workout_name'],
            date=datetime.strptime(data.get('date', datetime.now().strftime('%Y-%m-%d')), '%Y-%m-%d').date(),
            time=data.get('time', datetime.now().strftime('%H:%M'))
        )
        workout.set_exercises_data(data['exercises'])
        
        db.session.add(workout)
        db.session.commit()
        
        return jsonify({
            'message': 'Treino salvo com sucesso',
            'workout': workout.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@workout_bp.route('/history/<int:workout_id>', methods=['DELETE'])
@token_required
def delete_workout(current_user, workout_id):
    try:
        # Buscar treino do usuário
        workout = WorkoutHistory.query.filter_by(id=workout_id, user_id=current_user.id).first()
        
        if not workout:
            return jsonify({'message': 'Treino não encontrado'}), 404
        
        db.session.delete(workout)
        db.session.commit()
        
        return jsonify({'message': 'Treino removido com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

@workout_bp.route('/history/clear', methods=['DELETE'])
@token_required
def clear_workout_history(current_user):
    try:
        # Remover todo o histórico do usuário
        WorkoutHistory.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        return jsonify({'message': 'Histórico limpo com sucesso'}), 200
        
    except Exception as e:
        return jsonify({'message': f'Erro interno: {str(e)}'}), 500

