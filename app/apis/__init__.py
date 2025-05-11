def init_apis(app):
    from app.apis.dashboard import init_api_dashboard
    from app.apis.notification import init_api_notification
    from app.apis.studyduration import init_api_studyduration
    from app.apis.studyplan import init_api_studyplan
    from app.apis.profile import init_api_profile
    
    init_api_dashboard(app)
    init_api_notification(app)
    init_api_studyduration(app)
    init_api_studyplan(app)
    init_api_profile(app)



