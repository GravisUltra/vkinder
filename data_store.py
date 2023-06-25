# импорты
import sqlalchemy as sq
from sqlalchemy.orm import declarative_base
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import Session
from config import db_url_object


# схема БД
metadata = MetaData()
Base = declarative_base()

class Viewed(Base):
    __tablename__ = 'viewed'
    user_id = sq.Column(sq.Integer, primary_key=True)
    profile_id = sq.Column(sq.Integer, primary_key=True)



# инициализация объектов для работы с БД
engine = create_engine(db_url_object)
Base.metadata.create_all(engine)

# добавление записи в бд
def add_profile(user, profile):
    with Session(engine) as session:
        to_bd = Viewed(user_id=user, profile_id=profile)
        session.add(to_bd)
        session.commit()

# извлечение записей из БД; функция не используется
def get_profile(user, profile):
    result = []
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(Viewed.user_id==user).filter(Viewed.profile_id==profile).all()
    return(from_bd)

# проверка профиля на предмет его наличия в списке ранее просмотренных пользователем профилей.
def profile_is_viewed_by(profile_id, user_id):
    with Session(engine) as session:
        from_bd = session.query(Viewed).filter(
            Viewed.user_id == user_id,
            Viewed.profile_id == profile_id
        ).first()
    return True if from_bd else False



if __name__ == "__main__":
    # add_profile(2, 1)
    # print(get_profile(1, 1))
    
    # for item in get_profile(1, 1):
    #     print(f"Анкета {item.profile_id} просмотрена пользователем {item.user_id}")
    
    print(profile_is_viewed_by(1, 1))