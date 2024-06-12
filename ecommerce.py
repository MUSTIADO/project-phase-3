import argparse
import logging
from sqlalchemy.orm import Session
from models import User, Product, CartItem, Order, OrderItem, OrderStatus, UserRole, Session as DBSession, engine

# Set up logging
logging.basicConfig(filename='ecommerce.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Register user
def register(username, password, role=UserRole.USER):
    try:
        with DBSession() as session:
            if session.query(User).filter_by(username=username).first():
                print("Username already exists.")
                return
            user = User(username=username, password=password, role=role)
            session.add(user)
            session.commit()
            print("User registered successfully.")
            logging.info(f"User registered: {username} as {role.value}")
    except Exception as e:
        print("An error occurred while registering the user.")
        logging.error(f"Error registering user: {e}")

# Login user
def login(username, password):
    try:
        with DBSession() as session:
            user = session.query(User).filter_by(username=username, password=password).first()
            if user:
                with open('session.txt', 'w') as file:
                    file.write(f"{username},{user.role.value}")
                print("Logged in successfully.")
                logging.info(f"User logged in: {username}")
                if user.role == UserRole.ADMIN:
                    print("Welcome Admin!")
                else:
                    print("Welcome User!")
            else:
                print("Invalid username or password.")
    except Exception as e:
        print("An error occurred while logging in.")
        logging.error(f"Error logging in user: {e}")

# Logout user
def logout():
    try:
        with open('session.txt', 'w') as file:
            file.write('')
        print("Logged out successfully.")
        logging.info("User logged out.")
    except Exception as e:
        print("An error occurred while logging out.")
        logging.error(f"Error logging out user: {e}")

# Get current user
def get_current_user():
    try:
        with open('session.txt', 'r') as file:
            data = file.read().strip().split(',')
        if not data or len(data) != 2:
            return None
        username, role = data
        with DBSession() as session:
            return session.query(User).filter_by(username=username, role=UserRole(role)).first()
    except Exception as e:
        logging.error(f"Error getting current user: {e}")
        return None

# Restrict certain actions to admins
def admin_required(func):
    def wrapper(*args, **kwargs):
        user = get_current_user()
        if not user or user.role != UserRole.ADMIN:
            print("Admin access required.")
            return
        return func(*args, **kwargs)
    return wrapper

# Add new product (admin only)
@admin_required
def add_product(name, price):
    try:
        with DBSession() as session:
            product = Product(name=name, price=price)
            session.add(product)
            session.commit()
            print(f"Product '{name}' added successfully with price ${price}.")
            logging.info(f"Product added: {name}, Price: ${price}")
    except Exception as e:
        print("An error occurred while adding the product.")
        logging.error(f"Error adding product: {e}")

# List users (admin only)
@admin_required
def list_users():
    try:
        with DBSession() as session:
            users = session.query(User).all()
            for user in users:
                print(f"User ID: {user.id}, Username: {user.username}, Role: {user.role.value}")
    except Exception as e:
        print("An error occurred while listing users.")
        logging.error(f"Error listing users: {e}")

# Delete user (admin only)
@admin_required
def delete_user(user_id):
    try:
        with DBSession() as session:
            user = session.query(User).filter_by(id=user_id).first()
            if user:
                session.delete(user)
                session.commit()
                logging.info(f"User with ID {user_id} deleted.")
                return True
            else:
                logging.warning(f"User with ID {user_id} not found.")
                return False
    except Exception as e:
        logging.error(f"Error deleting user with ID {user_id}: {e}", exc_info=True)
        return False

# List products
def list_products():
    try:
        with DBSession() as session:
            products = session.query(Product).all()
            for product in products:
                print(f"Product ID: {product.id}, Name: {product.name}, Price: ${product.price}")
    except Exception as e:
        print("An error occurred while listing products.")
        logging.error(f"Error listing products: {e}")

# Add to cart
def add_to_cart(product_id):
    user = get_current_user()
    if not user:
        print("Please login first.")
        return
    try:
        with DBSession() as session:
            product = session.query(Product).filter_by(id=product_id).first()
            if not product:
                print("Product not found.")
                return
            cart_item = CartItem(user_id=user.id, product_id=product.id)
            session.add(cart_item)
            session.commit()
            print(f"Product '{product.name}' added to cart.")
            logging.info(f"Product added to cart: {product.name}, User: {user.username}")
    except Exception as e:
        print("An error occurred while adding to cart.")
        logging.error(f"Error adding to cart: {e}")

# View cart
def view_cart():
    user = get_current_user()
    if not user:
        print("Please login first.")
        return
    try:
        with DBSession() as session:
            cart_items = session.query(CartItem).filter_by(user_id=user.id).all()
            if not cart_items:
                print("Your cart is empty.")
                return
            for item in cart_items:
                product = session.query(Product).filter_by(id=item.product_id).first()
                print(f"Product ID: {product.id}, Name: {product.name}, Price: ${product.price}")
    except Exception as e:
        print("An error occurred while viewing the cart.")
        logging.error(f"Error viewing cart: {e}")

# Place order
def place_order():
    user = get_current_user()
    if not user:
        print("Please login first.")
        return

    try:
        with DBSession() as session:
            cart_items = session.query(CartItem).filter_by(user_id=user.id).all()
            if not cart_items:
                print("Your cart is empty. Please add items to your cart before placing an order.")
                return

            total = 0
            order_items = []
            for item in cart_items:
                product = session.query(Product).filter_by(id=item.product_id).first()
                total += product.price
                order_items.append(OrderItem(product_id=product.id, quantity=1, unit_price=product.price))

            order = Order(user_id=user.id, total=total, status=OrderStatus.PENDING)
            order.order_items = order_items
            session.add(order)
            session.commit()

            # Remove items from the cart after placing the order
            session.query(CartItem).filter_by(user_id=user.id).delete()
            
            print("Order placed successfully.")
            logging.info(f"Order placed: {order.id}, User: {user.username}")

    except Exception as e:
        print("An error occurred while placing the order.")
        logging.error(f"Error placing order: {e}")


# View orders
def view_orders():
    user = get_current_user()
    if not user:
        print("Please login first.")
        return
    try:
        with DBSession() as session:
            orders = session.query(Order).filter_by(user_id=user.id).all()
            if not orders:
                print("You have no orders.")
                return
            for order in orders:
                print(f"Order ID: {order.id}, Status: {order.status.value}")
                order_items = session.query(OrderItem).filter_by(order_id=order.id).all()
                for item in order_items:
                    product = session.query(Product).filter_by(id=item.product_id).first()
                    print(f"  Product ID: {product.id}, Name: {product.name}, Price: ${product.price}, Quantity: {item.quantity}")
    except Exception as e:
        print("An error occurred while viewing orders.")
        logging.error(f"Error viewing orders: {e}")

# Cancel order
def cancel_order(order_id):
    user = get_current_user()
    if not user:
        print("Please login first.")
        return
    try:
        with DBSession() as session:
            order = session.query(Order).filter_by(id=order_id, user_id=user.id).first()
            if not order:
                print("Order not found.")
                return
            if order.status != OrderStatus.PENDING:
                print("Only pending orders can be canceled.")
                return
            order.status = OrderStatus.CANCELED
            session.commit()
            print("Order canceled successfully.")
            logging.info(f"Order canceled: {order_id}, User: {user.username}")
    except Exception as e:
        print("An error occurred while canceling the order.")
        logging.error(f"Error canceling order: {e}")

# Update order status (admin only)
@admin_required
def update_order_status(order_id, status):
    try:
        with DBSession() as session:
            order = session.query(Order).filter_by(id=order_id).first()
            if not order:
                print("Order not found.")
                return
            order.status = status
            session.commit()
            print(f"Order status updated to {status.value}.")
            logging.info(f"Order status updated: {order_id}, Status: {status.value}")
    except Exception as e:
        print("An error occurred while updating the order status.")
        logging.error(f"Error updating order status: {e}")
def main():
    while True:
        user = get_current_user()

        print("\nChoose an action:")
        print("1. Register")
        print("2. Login")
        print("3. Logout")
        print("4. List Users (Admin Only)")
        print("5. Add Product (Admin Only)")
        print("6. List Products")
        print("7. Add to Cart")
        print("8. View Cart")
        print("9. Place Order")
        print("10. View Orders")
        print("11. Cancel Order")
        print("12. Update Order Status (Admin Only)")
        print("13. Delete User (Admin Only)")
        print("14. Exit")
        
        choice = input("Enter your choice: ")

        if choice == '1':
            username = input("Enter username: ")
            password = input("Enter password: ")
            role_input = input("Enter role (user/admin): ").strip().lower()
            role = UserRole.ADMIN if role_input == "admin" else UserRole.USER
            register(username, password, role)
        elif choice == '2':
            username = input("Enter username: ")
            password = input("Enter password: ")
            login(username, password)
        elif choice == '3':
            logout()
        elif choice == '4':
            if user and user.role == UserRole.ADMIN:
                list_users()
            else:
                print("Admin access required.")
        elif choice == '5':
            if user and user.role == UserRole.ADMIN:
                name = input("Enter product name: ")
                price = float(input("Enter product price: "))
                add_product(name, price)
            else:
                print("Admin access required.")
        elif choice == '6':
            list_products()
        elif choice == '7':
            product_id = int(input("Enter product ID to add to cart: "))
            add_to_cart(product_id)
        elif choice == '8':
            view_cart()
        elif choice == '9':
            place_order()
        elif choice == '10':
            view_orders()
        elif choice == '11':
            order_id = int(input("Enter order ID to cancel: "))
            cancel_order(order_id)
        elif choice == '12':
            if user and user.role == UserRole.ADMIN:
                order_id = int(input("Enter order ID to update: "))
                status = input("Enter new status (pending, shipped, delivered, canceled): ").upper()
                status_enum = OrderStatus[status]
                update_order_status(order_id, status_enum)
            else:
                print("Admin access required.")
        elif choice == '13':
            if user and user.role == UserRole.ADMIN:
                user_id = int(input("Enter user ID to delete: "))
                if delete_user(user_id):
                    print(f"User ID: {user_id} deleted successfully.")
                else:
                    print(f"Failed to delete User ID: {user_id}.")
            else:
                print("Admin access required.")
        elif choice == '14':
            print("Exiting the application.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
