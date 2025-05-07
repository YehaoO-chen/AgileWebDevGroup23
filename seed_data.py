from app import create_app, db
from app.models import User, StudyPlan, StudyDuration, Notification
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    # 1. 检查是否已存在该用户
    existing = User.query.filter_by(username='ABCDEF').first()
    if existing:
        print("User 'ABCDEF' already exists. Aborting to avoid duplicate.")
        exit()

    # 2. 创建用户
    user = User(username='ABCDEF', password='123456', security_answer='answer')
    db.session.add(user)
    db.session.commit()
    print(f"Created user with id={user.id}")

    # 3. 插入写死的学习时长，共 100 分钟，今天 30 分钟
    now = datetime.utcnow()

    # 70 分钟历史记录
    study_data = [
        (now - timedelta(days=3), 20),
        (now - timedelta(days=2), 25),
        (now - timedelta(days=1), 25),
    ]

    for start_time, duration in study_data:
        db.session.add(StudyDuration(
            user_id=user.id,
            duration=duration,
            start_time=start_time,
            end_time=start_time + timedelta(minutes=duration),
            stop_times=0
        ))

    # 30 分钟今天记录
    today_start = now.replace(hour=9, minute=0, second=0, microsecond=0)
    db.session.add(StudyDuration(
        user_id=user.id,
        duration=30,
        start_time=today_start,
        end_time=today_start + timedelta(minutes=30),
        stop_times=0
    ))

    print("Inserted total 100 minutes (30 today) study duration")

    # 4. 插入计划（不是必须）
    db.session.add(StudyPlan(
        user_id=user.id,
        title='Mock Plan',
        content='Practice Python',
        create_time=now - timedelta(days=1),
        status=0
    ))

    # 5. 插入一条通知
    db.session.add(Notification(
        sender_id=user.id,
        receiver_id=user.id,
        content='Welcome ABCDEF!',
        send_time=now,
        status=0
    ))

    # 6. 提交所有更改
    db.session.commit()
    print("Seed data for 'ABCDEF' inserted successfully.")
