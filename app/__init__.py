from flask import Flask
from flask_assets import Environment, Bundle
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit
from config import Config


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    from app.extensions import db
    db.init_app(app)
    
    # Setup Flask-Assets
    assets = Environment(app)
    assets.url = app.static_url_path
    
    # Register individual SCSS bundles
    main_scss = Bundle('scss/main.scss', filters='libsass', output='css/main.css')
    cart_scss = Bundle('scss/cart.scss', filters='libsass', output='css/cart.css')
    checkout_scss = Bundle('scss/checkout.scss', filters='libsass', output='css/checkout.css')
    detail_scss = Bundle('scss/detail.scss', filters='libsass', output='css/detail.css')
    admin_scss = Bundle('scss/admin.scss', filters='libsass', output='css/admin.css')
    
    assets.register('main_css', main_scss)
    assets.register('cart_css', cart_scss)
    assets.register('checkout_css', checkout_scss)
    assets.register('detail_css', detail_scss)
    assets.register('admin_css', admin_scss)
    
    # Import models before creating tables
    from app.models import listing, access_log  # noqa: F401
    
    # Create database tables
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables created")
    
    # Initialize access logging middleware
    from app.middleware.access_logger import init_access_logging
    init_access_logging(app)
    
    # Register blueprints
    from app.routes import api, main
    app.register_blueprint(api.bp)
    app.register_blueprint(main.bp)
    
    # Setup scheduled sync if enabled
    if app.config.get('ENABLE_AUTO_SYNC') and app.config.get('DISCOGS_TOKEN'):
        setup_scheduler(app)
    else:
        if not app.config.get('DISCOGS_TOKEN'):
            app.logger.warning("DISCOGS_TOKEN not set. Auto-sync disabled.")
        else:
            app.logger.info("Auto-sync is disabled. Set ENABLE_AUTO_SYNC=true to enable.")
    
    return app


def setup_scheduler(app):
    """Setup APScheduler for periodic Discogs sync."""
    from app.services.discogs_sync_service import DiscogsSyncService
    
    scheduler = BackgroundScheduler()
    
    def sync_job():
        """Job to sync Discogs listings."""
        with app.app_context():
            try:
                app.logger.info("Starting scheduled Discogs sync...")
                sync_service = DiscogsSyncService(
                    token=app.config['DISCOGS_TOKEN'],
                    seller_username=app.config['DISCOGS_SELLER_USERNAME'],
                    user_agent=app.config['DISCOGS_USER_AGENT']
                )
                stats = sync_service.sync_all_listings()
                app.logger.info(f"Sync completed: {stats}")
            except Exception as e:
                app.logger.error(f"Error during scheduled sync: {e}")
    
    # Schedule the job to run every N hours
    interval_hours = app.config.get('SYNC_INTERVAL_HOURS', 1)
    scheduler.add_job(
        func=sync_job,
        trigger=IntervalTrigger(hours=interval_hours),
        id='discogs_sync_job',
        name='Sync Discogs listings',
        replace_existing=True
    )
    
    # Start the scheduler
    scheduler.start()
    app.logger.info(f"Scheduler started. Sync interval: {interval_hours} hour(s)")
    
    # Schedule initial sync to run in background after 5 seconds
    def initial_sync():
        """Run initial sync in background."""
        import time
        time.sleep(5)  # Wait for server to start
        with app.app_context():
            try:
                app.logger.info("Running initial Discogs sync...")
                sync_service = DiscogsSyncService(
                    token=app.config['DISCOGS_TOKEN'],
                    seller_username=app.config['DISCOGS_SELLER_USERNAME'],
                    user_agent=app.config['DISCOGS_USER_AGENT']
                )
                stats = sync_service.sync_all_listings()
                app.logger.info(f"Initial sync completed: {stats}")
            except Exception as e:
                app.logger.error(f"Error during initial sync: {e}")
    
    # Run initial sync in background thread
    from threading import Thread
    sync_thread = Thread(target=initial_sync, daemon=True)
    sync_thread.start()
    app.logger.info("Initial sync scheduled to run in background...")
    
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())
