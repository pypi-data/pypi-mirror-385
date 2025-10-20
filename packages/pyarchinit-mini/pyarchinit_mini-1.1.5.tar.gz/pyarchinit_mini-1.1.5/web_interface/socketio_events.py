"""
WebSocket event handlers for real-time collaboration
"""

from flask import request
from flask_socketio import emit, join_room, leave_room
from flask_login import current_user
from datetime import datetime
from typing import Dict, List

# Store online users: {sid: {username, user_id, connected_at}}
online_users: Dict[str, dict] = {}


def init_socketio_events(socketio):
    """
    Initialize WebSocket event handlers

    Args:
        socketio: Flask-SocketIO instance
    """

    @socketio.on('connect')
    def handle_connect():
        """Handle client connection"""
        if not current_user.is_authenticated:
            return False  # Reject unauthenticated connections

        sid = request.sid
        online_users[sid] = {
            'username': current_user.username,
            'user_id': current_user.id,
            'role': current_user.role,
            'connected_at': datetime.utcnow().isoformat()
        }

        print(f"[WebSocket] User connected: {current_user.username} (SID: {sid})")

        # Notify all clients about new user
        emit('user_joined', {
            'username': current_user.username,
            'user_id': current_user.id,
            'role': current_user.role,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=sid)

        # Send current online users to the new client
        emit('online_users', {
            'users': [
                {
                    'username': user['username'],
                    'user_id': user['user_id'],
                    'role': user['role']
                }
                for user in online_users.values()
            ]
        })

    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle client disconnection"""
        sid = request.sid

        if sid in online_users:
            user_info = online_users.pop(sid)
            print(f"[WebSocket] User disconnected: {user_info['username']} (SID: {sid})")

            # Notify all clients about user leaving
            emit('user_left', {
                'username': user_info['username'],
                'user_id': user_info['user_id'],
                'timestamp': datetime.utcnow().isoformat()
            }, broadcast=True)

    @socketio.on('get_online_users')
    def handle_get_online_users():
        """Send list of online users to requesting client"""
        emit('online_users', {
            'users': [
                {
                    'username': user['username'],
                    'user_id': user['user_id'],
                    'role': user['role']
                }
                for user in online_users.values()
            ]
        })

    @socketio.on('site_created')
    def handle_site_created(data):
        """Broadcast site creation"""
        if not current_user.is_authenticated:
            return

        emit('site_created', {
            'site_name': data.get('site_name'),
            'site_id': data.get('site_id'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('site_updated')
    def handle_site_updated(data):
        """Broadcast site update"""
        if not current_user.is_authenticated:
            return

        emit('site_updated', {
            'site_name': data.get('site_name'),
            'site_id': data.get('site_id'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('site_deleted')
    def handle_site_deleted(data):
        """Broadcast site deletion"""
        if not current_user.is_authenticated:
            return

        emit('site_deleted', {
            'site_name': data.get('site_name'),
            'site_id': data.get('site_id'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('us_created')
    def handle_us_created(data):
        """Broadcast US creation"""
        if not current_user.is_authenticated:
            return

        emit('us_created', {
            'site': data.get('site'),
            'us_number': data.get('us_number'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('us_updated')
    def handle_us_updated(data):
        """Broadcast US update"""
        if not current_user.is_authenticated:
            return

        emit('us_updated', {
            'site': data.get('site'),
            'us_number': data.get('us_number'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('us_deleted')
    def handle_us_deleted(data):
        """Broadcast US deletion"""
        if not current_user.is_authenticated:
            return

        emit('us_deleted', {
            'site': data.get('site'),
            'us_number': data.get('us_number'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('inventario_created')
    def handle_inventario_created(data):
        """Broadcast inventario creation"""
        if not current_user.is_authenticated:
            return

        emit('inventario_created', {
            'numero_inventario': data.get('numero_inventario'),
            'site': data.get('site'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('inventario_updated')
    def handle_inventario_updated(data):
        """Broadcast inventario update"""
        if not current_user.is_authenticated:
            return

        emit('inventario_updated', {
            'numero_inventario': data.get('numero_inventario'),
            'site': data.get('site'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)

    @socketio.on('inventario_deleted')
    def handle_inventario_deleted(data):
        """Broadcast inventario deletion"""
        if not current_user.is_authenticated:
            return

        emit('inventario_deleted', {
            'numero_inventario': data.get('numero_inventario'),
            'site': data.get('site'),
            'user': current_user.username,
            'timestamp': datetime.utcnow().isoformat()
        }, broadcast=True, skip_sid=request.sid)


def broadcast_site_created(socketio, site_name, site_id):
    """Helper to broadcast site creation from server side"""
    socketio.emit('site_created', {
        'site_name': site_name,
        'site_id': site_id,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_site_updated(socketio, site_name, site_id):
    """Helper to broadcast site update from server side"""
    socketio.emit('site_updated', {
        'site_name': site_name,
        'site_id': site_id,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_us_created(socketio, site, us_number):
    """Helper to broadcast US creation from server side"""
    socketio.emit('us_created', {
        'site': site,
        'us_number': us_number,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_site_deleted(socketio, site_name, site_id):
    """Helper to broadcast site deletion from server side"""
    socketio.emit('site_deleted', {
        'site_name': site_name,
        'site_id': site_id,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_us_updated(socketio, site, us_number):
    """Helper to broadcast US update from server side"""
    socketio.emit('us_updated', {
        'site': site,
        'us_number': us_number,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_us_deleted(socketio, site, us_number):
    """Helper to broadcast US deletion from server side"""
    socketio.emit('us_deleted', {
        'site': site,
        'us_number': us_number,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_inventario_created(socketio, numero_inventario, site):
    """Helper to broadcast inventario creation from server side"""
    socketio.emit('inventario_created', {
        'numero_inventario': numero_inventario,
        'site': site,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_inventario_updated(socketio, numero_inventario, site):
    """Helper to broadcast inventario update from server side"""
    socketio.emit('inventario_updated', {
        'numero_inventario': numero_inventario,
        'site': site,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })


def broadcast_inventario_deleted(socketio, numero_inventario, site):
    """Helper to broadcast inventario deletion from server side"""
    socketio.emit('inventario_deleted', {
        'numero_inventario': numero_inventario,
        'site': site,
        'user': current_user.username if current_user.is_authenticated else 'System',
        'timestamp': datetime.utcnow().isoformat()
    })
