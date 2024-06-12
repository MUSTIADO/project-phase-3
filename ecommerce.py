import argparse
import logging
from sqlalchemy.orm import Session
from models import User, Product, CartItem, Order, OrderItem, OrderStatus, Session as DBSession, engine

# Set up logging
logging.basicConfig(filename='ecommerce.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Register user
def register(username, password):
    try:
        with DBSession() as session:
            if session.query(User).filter_by(username=username).first():
                print("Username already exists.")
                return
            user = User(username=username, password=password)
            session.add(user)
            session.commit()
            print("User registered successfully.")
            logging.info(f"User registered: {username}")
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
                    file.write(username)
                print("Logged in successfully.")
                logging.info(f"User logged in: {username}")
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
            username = file.read().strip()
        if not username:
            return None
        with DBSession() as session:
            return session.query(User).filter_by(username=username).first()
    except Exception as e:
        logging.error(f"Error getting current user: {e}")
        return None

# Add new product
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

# List products
def list_products(product_id=None):
    try:
        with DBSession() as session:
            if product_id:
                product = session.query(Product).filter_by(id=product_id).first()
                if product:
                    print(f"Product ID: {product.id}, Name: {product.name}, Price: ${product.price}")
                else:
                    print("Product not found.")
            else:
                products = session.query(Product).all()
                for product in products:
                    print(f"Product ID: {product.id}, Name: {product.name}, Price: ${product.price}")
    except Exception as e:
        print("An error occurred while listing products.")
        logging.error(f"Error listing products: {e}")

# List users
def list_users():
    try:
        with DBSession() as session:
            users = session.query(User).all()
            for user in users:
                print(f"User ID: {user.id}, Username: {user.username}")
    except Exception as e:
        print("An error occurred while listing users.")
        logging.error(f"Error listing users: {e}")

# Add product to cart
def add_to_cart(product_id):
    user = get_current_user()
    if not user:
        print("Please log in first.")
        return

    try:
        with DBSession() as session:
            product = session.query(Product).filter_by(id=product_id).first()
            if product:
                cart_item = CartItem(user_id=user.id, product_id=product.id)
                session.add(cart_item)
                session.commit()
                print(f"Added {product.name} to the cart.")
                logging.info(f"Product {product.name} added to cart for user {user.username}.")
            else:
                print("Product not found.")
    except Exception as e:
        print("An error occurred while adding the product to the cart.")
        logging.error(f"Error adding product to cart: {e}")

# View cart
def view_cart():
    user = get_current_user()
    if not user:
        print("Please log in first.")
        return

    try:
        with DBSession() as session:
            cart_items = session.query(CartItem).filter_by(user_id=user.id).all()
            if not cart_items:
                print("Your cart is empty.")
            else:
                total = 0
                for item in cart_items:
                    product = session.query(Product).filter_by(id=item.product_id).first()
                    print(f"{product.name} - ${product.price}")
                    total += product.price
                print(f"Total: ${total}")
                logging.info(f"Cart viewed for user {user.username}. Total: ${total}")
    except Exception as e:
        print("An error occurred while viewing the cart.")
        logging.error(f"Error viewing cart: {e}")

# Place an order
def place_order():
    user = get_current_user()
    if not user:
        print("Please log in first.")
        return

    try:
        with DBSession() as session:
            cart_items = session.query(CartItem).filter_by(user_id=user.id).all()
            if not cart_items:
                print("Your cart is empty.")
            else:
                total = sum(session.query(Product).filter_by(id=item.product_id).first().price for item in cart_items)
                order = Order(user_id=user.id, total=total)
                session.add(order)
                session.commit()
                for item in cart_items:
                    order_item = OrderItem(order_id=order.id, product_id=item.product_id, quantity=1)
                    session.add(order_item)
                    session.delete(item)
                session.commit()
                print(f"Order placed successfully with total amount ${total}. Your cart is now empty.")
                logging.info(f"Order placed for user {user.username}. Total: ${total}")
    except Exception as e:
        print("An error occurred while placing the order.")
        logging.error(f"Error placing order: {e}")

# View orders
def view_orders():
    user = get_current_user()
    if not user:
        print("Please log in first.")
        return

    try:
        with DBSession() as session:
            orders = session.query(Order).filter_by(user_id=user.id).all()
            for order in orders:
                print(f"Order ID: {order.id}, Total: ${order.total}, Status: {order.status.value}, Created at: {order.created_at}")
                for item in order.order_items:
                    product = session.query(Product).filter_by(id=item.product_id).first()
                    print(f"  Product ID: {product.id}, Name: {product.name}, Quantity: {item.quantity}")
            logging.info(f"Orders viewed for user {user.username}.")
    except Exception as e:
        print("An error occurred while viewing orders.")
        logging.error(f"Error viewing orders: {e}")

# Cancel an order
def cancel_order(order_id):
    user = get_current_user()
    if not user:
        print("Please log in first.")
        return

    try:
        with DBSession() as session:
            order = session.query(Order).filter_by(id=order_id, user_id=user.id).first()
            if order:
                if order.status == OrderStatus.PENDING:
                    order.status = OrderStatus.CANCELED
                    session.commit()
                    print(f"Order {order_id} has been canceled.")
                    logging.info(f"Order {order_id} canceled for user {user.username}.")
                else:
                    print("Only pending orders can be canceled.")
            else:
                print("Order not found.")
    except Exception as e:
        print("An error occurred while canceling the order.")
        logging.error(f"Error canceling order: {e}")

# Update order status
def update_order_status(order_id, status):
    user = get_current_user()
    if not user:
        print("Please log in first.")
        return

    try:
        with DBSession() as session:
            order = session.query(Order).filter_by(id=order_id, user_id=user.id).first()
            if order:
                status_normalized = status.upper()
                if status_normalized in OrderStatus.__members__:
                    order.status = OrderStatus[status_normalized]
                    session.commit()
                    updated_status = order.status.name
                    print(f"Order {order_id} status has been updated to {updated_status}.")
                    logging.info(f"Order {order_id} status updated to {updated_status} for user {user.username}.")
                else:
                    print("Invalid status.")
            else:
                print("Order not found.")
    except Exception as e:
        print("An error occurred while updating the order status.")
        logging.error(f"Error updating order status: {e}")

# Check database content
def check_database_content():
    try:
        with DBSession() as session:
            print("Users:")
            users = session.query(User).all()
            for user in users:
                print(f"User ID: {user.id}, Username: {user.username}")

            print("\nProducts:")
            products = session.query(Product).all()
            for product in products:
                print(f"Product ID: {product.id}, Name: {product.name}, Price: ${product.price}")

            print("\nCart Items:")
            cart_items = session.query(CartItem).all()
            for item in cart_items:
                print(f"CartItem ID: {item.id}, User ID: {item.user_id}, Product ID: {item.product_id}")

            print("\nOrders:")
            orders = session.query(Order).all()
            for order in orders:
                print(f"Order ID: {order.id}, User ID: {order.user_id}, Total: ${order.total}, Status: {order.status}, Created at: {order.created_at}")

            print("\nOrder Items:")
            order_items = session.query(OrderItem).all()
            for item in order_items:
                print(f"OrderItem ID: {item.id}, Order ID: {item.order_id}, Product ID: {item.product_id}, Quantity: {item.quantity}")
    except Exception as e:
        print("An error occurred while checking database content.")
        logging.error(f"Error checking database content: {e}")

# Delete user
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
def main():
    while True:
        print("Choose an action:")
        print("1. Register")
        print("2. Login")
        print("3. Logout")
        print("4. List Users")
        print("5. Add Product")
        print("6. List Products")
        print("7. Add to Cart")
        print("8. View Cart")
        print("9. Place Order")
        print("10. View Orders")
        print("11. Cancel Order")
        print("12. Update Order Status")
        print("13. Delete User")
        print("14. Check The Database")
        print("15. Exit")

        action = input("> ")

        if action == '1':
            username = input("Enter username: ")
            password = input("Enter password: ")
            register(username, password)
        elif action == '2':
            username = input("Enter username: ")
            password = input("Enter password: ")
            login(username, password)
        elif action == '3':
            logout()
        elif action == '4':
            list_users()
        elif action == '5':
            name = input("Enter the product name: ")
            price = float(input("Enter the product price: "))
            add_product(name, price)
        elif action == '6':
            list_products()
        elif action == '7':
            product_id = input("Enter the product ID to add to cart: ")
            add_to_cart(int(product_id))
        elif action == '8':
            view_cart()
        elif action == '9':
            place_order()
        elif action == '10':
            view_orders()
        elif action == '11':
            order_id = input("Enter the order ID to cancel: ")
            cancel_order(int(order_id))
        elif action == '12':
            order_id = input("Enter the order ID: ")
            status = input("Enter the new status: ")
            update_order_status(int(order_id), status)
        # elif action == '13':
        #     user_id = input("Enter the user ID to delete: ")
        #     try:
        #        user_id = int(user_id)
        #        with DBSession() as session:
        #            user = session.query(User).filter_by(id=user_id).first()
        #            if user:
        #                 session.delete(user)
        #                 session.commit()
        #                 print(f"User with ID {user_id} has been deleted successfully.")
        #                 logging.info(f"User with ID {user_id} deleted.")
        #            else:
        #                 print("User not found.")
        #                 logging.warning(f"User with ID {user_id} not found.")

            # except ValueError:
            #     print("Invalid user ID. Please enter a valid integer.")
            #     logging.error("Invalid user ID provided for deletion.")
            # except Exception as e:
            #     print("An error occurred while deleting the user.")
            #     logging.error(f"Error deleting user: {e}")
        
        elif action == '13':
             user_id = input("Enter the user ID to delete: ")
             if delete_user(int(user_id)):
                 print(f"User with ID {user_id} has been deleted successfully.")
        # Update and remove user from your application
             else:
                 print(f"Failed to delete user with ID {user_id}.")


        
        elif action == '14':
            check_database_content()
        elif action == '15':
            print("Exiting the application.")
            break  # Exit the loop and end the program
        else:
            print("Invalid action number. Please choose a number between 1 and 15.")

if __name__ == '__main__':
    main()
