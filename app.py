import datetime
import sqlalchemy
from aiohttp import web, ClientSession
import aiohttp
import asyncio
import sys
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
from aiohttp_basicauth import BasicAuthMiddleware

Base = declarative_base()
# auth = BasicAuthMiddleware(username='user', password='password', force=False)

class Advertisement(Base):
    __tablename__ = 'advertisement'
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    description = Column(String(300), nullable=False)
    date = Column(DateTime, default=datetime)
    creator = Column(String(300), nullable=False)

    def __repr__(self):
        return f'Объявление {self.title}, {self.description}, {self.creator}, {self.date}'


engine = create_engine('sqlite:///aiohttp.db')
DBSession = sessionmaker(bind=engine)
Base.metadata.create_all(engine)
routes = web.RouteTableDef()


users = {
    "user1": generate_password_hash("zxcvbnbnmm1"),
    "user2": generate_password_hash("zxcvbnbnmm2"),
    "user3": generate_password_hash("zxcvbnbnmm3")
}
class CustomBasicAuth(BasicAuthMiddleware):
    async def check_credentials(self, username, password, request):
        print(username, 1)
        print(password)
        if username in users and \
                check_password_hash(users.get(username), password):
            return username
auth = CustomBasicAuth()
app = web.Application(middlewares=[auth])

@routes.get('/home')
@auth.required
async def home(request):
    user = auth.user()
    return web.Response(text=f'hello {user}')


@routes.post('/create-advertisement')
@auth.required
async def create_advertisement(request):
    db_session = DBSession()
    new_advertisement = await request.json()
    if not new_advertisement or "title" not in new_advertisement:
        raise web.HTTPBadRequest(reason='Ошибка в запросе')

    title = new_advertisement["title"]
    print(title, 1)
    description = new_advertisement["description"]
    print(description, 2)
    date = datetime.datetime.utcnow()
    print(date)
    creator = new_advertisement.get('username', 'Stranger')
    print(creator)
    new_advertisement = Advertisement(title=title, description=description, date=date, creator=creator)
    print(new_advertisement)
    async with aiohttp.ClientSession():
            db_session.add(new_advertisement)
            db_session.commit()

app.add_routes(routes)

if __name__ == '__main__':
    web.run_app(app, host='127.0.0.1', port=8000)
