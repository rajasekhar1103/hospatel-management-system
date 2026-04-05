from flask import Flask, jsonify, request, g
from flask_compress import Compress
from extensions import db, jwt, redis_client, celery
from config import Config
import time
import uuid

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Compress(app)

    # Initialize extensions with app
    db.init_app(app)
    jwt.init_app(app)
    redis_client.init_app(app)
    celery.conf.update(app.config)
    
    # Track request timing
    @app.before_request
    def before_request():
        g.start_time = time.time()
        g.request_id = str(uuid.uuid4())[:8]
    
    @app.after_request
    def after_request(response):
        if hasattr(g, 'start_time'):
            elapsed = time.time() - g.start_time
            response.headers['X-Response-Time'] = f"{elapsed:.3f}s"
            response.headers['X-Request-ID'] = g.request_id
        return response
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy', 'timestamp': time.time()}), 200

    # Register blueprints (routes) using absolute imports
    from routes import auth, admin, doctor, patient
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    app.register_blueprint(doctor.bp, url_prefix='/api/doctor')
    app.register_blueprint(patient.bp, url_prefix='/api/patient')
    
    # Setup initial admin user and database creation
    with app.app_context():
        db.create_all()
        # Use absolute import for model functions
        from models.models import create_initial_admin
        create_initial_admin(db)
        
    # Serve VueJS index.html entry point (during production build)
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def serve(path):
        # NOTE: This only works if you build your Vue app (npm run build)
        return app.send_static_file('index.html')

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)