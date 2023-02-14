from sqlalchemy.exc import PendingRollbackError, IntegrityError
import asyncio

from db import session, User,Meets
import time
import datetime


def register_user(message,fio,department,group,course,user_type):
    username = message.from_user.username if message.from_user.username else None
    user = User(id=int(message.from_user.id), username=username,fio = fio,department = department,group = group , course = course, user_type = user_type)
    session.add(user)
    try:
        session.commit()
        return True
    except IntegrityError:
        session.rollback()  # откатываем session.add(user)
        return False

def select_user(user_id):
    user = session.query(User).filter(User.id == user_id).first()
    return user


def is_admin(user_id):
    user = session.query(User).filter(User.id == user_id).first()
    if user.user_type == 2:
        return True
    return False

def create_meet(message,professor_id,m_date,m_time,m_desc):
    user_id = message.from_user.id
    meet = Meets(user_id=user_id,professor_id = professor_id,m_date = m_date, m_time = m_time,m_desc=m_desc,create_time = time.time(),status = 0)
    session.add(meet)
    try:
        session.commit()
        return True,meet.id
    except IntegrityError:
        session.rollback()  # откатываем session.add(user)
        return False

def update_meet_status(meet_id,new_status):
    meet = session.query(Meets).filter(Meets.id == meet_id).first()
    if meet.status != 3:
        meet.status = new_status
        try:
            session.commit()
            return True
        except IntegrityError:
            session.rollback()  # откатываем session.add(user)
            return False
    else:
        return 3

def get_time_list(m_date,professor_id):
    meet = session.query(Meets).filter(Meets.m_date == m_date).filter(Meets.professor_id == professor_id).filter(Meets.status == 1).all()
    time_list = ['08:00', '08:30', '09:00', '09:30', '10:00', '10:30', '11:00', '11:30', '12:00', '12:30',
                 '13:00', '13:30', '14:00', '14:30', '15:30', '16:00', '16:30', '17:00', '17:30', '18:00',
                 '18:30', '19:00', '19:30', '20:00', '21:00', '21:30', '22:00', '22:30']
    result = [time_list.remove(i.m_time) for i in meet]
    return time_list

def get_user_id_from_meet(mc_id):
    meet = session.query(Meets).filter(Meets.id == mc_id).first()
    return meet.user_id

def get_meets(user_id):
    meet = session.query(Meets).filter(Meets.user_id == user_id).filter(Meets.status != 3).filter(Meets.m_date >= datetime.datetime.now().strftime("%d.%m.%Y")).all()
    return meet

def get_meets_p(user_id):
    meet = session.query(Meets).filter(Meets.professor_id == user_id).filter(Meets.status != 3).filter(Meets.status != 2).filter(Meets.m_date >= datetime.datetime.now().strftime("%d.%m.%Y")).all()
    return meet

print(get_meets_p('487310360'))