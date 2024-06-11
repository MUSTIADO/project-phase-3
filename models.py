from sqlalchemy import Column, Integer, String, Float, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime
import enum

Base = declarative_base()

class OrderStatus(enum.Enum):
    PENDING = "Pending"
    PROCESSED = "Processed"
    DELIVERED = "Delivered"
    CANCELED = "Canceled"

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    cart_items = relationship('CartItem', back_populates='user')
    orders = relationship('Order', back_populates='user')
# class User(Base):
#     __tablename__ = 'users'
#     id = Column(Integer, primary_key=True)
#     _username = Column(String, unique=True, nullable=False)
#     password = Column(String, nullable=False)
#     cart_items = relationship('CartItem', back_populates='user')
#     orders = relationship('Order', back_populates='user')

#     @property
#     def username(self):
#         return self._username

#     @username.setter
#     def username(self, value):
#         if not value:
#             raise ValueError("Username cannot be empty.")
#         self._username = value.strip()

#     @staticmethod
#     def create(username, password):
#         with Session() as session:
#             user = User(username=username, password=password)
#             session.add(user)
#             session.commit()
#             return user

    # @staticmethod
    # def delete(cls, user_id):
    #     with Session() as session:
    #         user = session.query(User).get(user_id)
    #         if user:
    #             session.delete(user)
    #             session.commit()
    #             print(f"User with ID {user_id} has been deleted.")
    #         else:
    #             print("User not found.")
#     @staticmethod
#     def get_all():
#         with Session() as session:
#             return session.query(User).all()

    # @staticmethod
    # def find_by_id(user_id):
    #     with Session() as session:
    #         return session.query(User).get(user_id)


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    cart_items = relationship('CartItem', back_populates='product')

class CartItem(Base):
    __tablename__ = 'cart_items'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    user = relationship('User', back_populates='cart_items')
    product = relationship('Product', back_populates='cart_items')

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    total = Column(Float, nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    user = relationship('User', back_populates='orders')
    order_items = relationship('OrderItem', back_populates='order')

class OrderItem(Base):
    __tablename__ = 'order_items'
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey('orders.id'), nullable=False)
    product_id = Column(Integer, ForeignKey('products.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    order = relationship('Order', back_populates='order_items')
    product = relationship('Product')

# Database setup
engine = create_engine('sqlite:///database.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
