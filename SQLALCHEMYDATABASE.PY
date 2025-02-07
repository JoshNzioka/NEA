import sqlalchemy as sa 
from sqlalchemy.orm import Mapped, mapped_column, sessionmaker, declarative_base
from prettytable import PrettyTable

db = sa.create_engine("sqlite:///:memory:")  # creating the database engine This creates an SQLite database in memory.
sessionFactory = sessionmaker(bind=db)  # creates a session using the session maker function that binds the database engine (db) to the session
Base = declarative_base()  # creates a base class used to define tables

class Products(Base):
    __tablename__ = "Products"
    productID: Mapped[int] = mapped_column(primary_key=True)
    productName: Mapped[str] = mapped_column()
    category: Mapped[str] = mapped_column()
    description: Mapped[str] = mapped_column()
    unitPrice: Mapped[int] = mapped_column()
    stockQuantity: Mapped[int] = mapped_column()
    supplier: Mapped[str] = mapped_column()
    dateAdded: Mapped[str] = mapped_column()

Base.metadata.create_all(db)

class Customers(Base):
    __tablename__ = "customers"
    customerID: Mapped[int] = mapped_column(primary_key=True)
    firstName: Mapped[str] = mapped_column()
    lastName: Mapped[str] = mapped_column()
    email: Mapped[str] = mapped_column()
    phone: Mapped[str] = mapped_column()
    address: Mapped[str] = mapped_column()
    city: Mapped[str] = mapped_column()
    county: Mapped[str] = mapped_column()
    postalCode: Mapped[str] = mapped_column()
    dateRegistered: Mapped[str] = mapped_column()
    orders = sa.orm.relationship("Orders", back_populates="customer")

class Orders(Base):
    __tablename__ = "Orders"
    orderID: Mapped[int] = mapped_column(primary_key=True)
    CustomerID: Mapped[int] = mapped_column(sa.ForeignKey("customers.customerID"))
    OrderDate: Mapped[str] = mapped_column()
    shippingAddress: Mapped[str] = mapped_column()
    totalPrice: Mapped[float] = mapped_column()
    orderStatus: Mapped[str] = mapped_column()
    customer = sa.orm.relationship('Customers', back_populates='orders')
    orderItems = sa.orm.relationship("OrderItems", back_populates="order")

class OrderItems(Base):
    __tablename__ = "OrderItems"
    orderItemID: Mapped[int] = mapped_column(primary_key=True)
    orderID: Mapped[int] = mapped_column(sa.ForeignKey("Orders.orderID"))
    productID: Mapped[int] = mapped_column(sa.ForeignKey("Products.productID"))
    quantity: Mapped[int] = mapped_column()
    unitPrice: Mapped[float] = mapped_column()
    order = sa.orm.relationship("Orders", back_populates="orderItems")
    product = sa.orm.relationship("Products")

class OrderedProductQuantity(Base):
    __tablename__ = "OrderedProductQuantity"
    id: Mapped[int] = mapped_column(primary_key=True)
    orderID: Mapped[int] = mapped_column(sa.ForeignKey("Orders.orderID"))
    productID: Mapped[int] = mapped_column(sa.ForeignKey("Products.productID"))
    quantityOrdered: Mapped[int] = mapped_column()

Base.metadata.create_all(db)

# PrettyTable section restored
order_details_table = PrettyTable()
order_details_table.field_names = ["Order ID", "Date", "Customer Name", "Customer Email", "Customer Phone", "Shipping Address", "Billing Address"]

product_details_table = PrettyTable()
product_details_table.field_names = ["Order ID", "Product Name", "Quantity Ordered", "Unit Price", "Total Price"]

order_status_table = PrettyTable()
order_status_table.field_names = ["Order ID", "Payment Status", "Order Status", "Shipment Date", "Delivery Date", "Notes"]

refund_table = PrettyTable()
refund_table.field_names = ["Order ID", "Return Requested", "Return Approved", "Refund Processed", "Reason for Return"]

# Function to get user input and populate tables
def get_user_input():
    with sessionFactory() as db_session:
        orderID = input("Enter Order ID: ")
        orderDate = input("Enter Order Date: ")
        customerName = input("Enter Customer Name: ")
        customerEmail = input("Enter Customer Email: ")
        customerPhone = input("Enter Customer Phone: ")
        shippingAddress = input("Enter Shipping Address: ")
        billingAddress = input("Enter Billing Address: ")
        
        # Creating a new customer
        new_customer = Customers(
            firstName=customerName.split()[0],  # Assuming first name is the first part
            lastName=customerName.split()[1] if len(customerName.split()) > 1 else "",  # Assuming last name is the second part
            email=customerEmail,
            phone=customerPhone,
            address=shippingAddress,
            city="N/A",  # Replace with actual logic to collect city and other address details
            county="N/A",  # Replace with actual logic for county
            postalCode="N/A",  # Replace with actual logic for postal code
            dateRegistered=orderDate
        )
        db_session.add(new_customer)
        db_session.commit()  # Committing customer data

        order_details_table.add_row([
            orderID, orderDate, customerName, customerEmail, customerPhone, shippingAddress, billingAddress
        ])
        
        # Collecting product info
        productID = input("Enter Product ID: ")
        productName = input("Enter Product Name: ")
        quantityOrdered = int(input("Enter Quantity Ordered: "))
        unitPrice = float(input("Enter Unit Price: "))
        totalPrice = quantityOrdered * unitPrice
        
        product_details_table.add_row([
            orderID, productName, quantityOrdered, unitPrice, totalPrice
        ])
        
        # Creating a new order
        new_order = Orders(
            orderID=orderID,
            CustomerID=new_customer.customerID,  # Assuming we need to link the order to the customer
            OrderDate=orderDate,
            shippingAddress=shippingAddress,
            totalPrice=totalPrice,
            orderStatus="Pending"  # Default status
        )
        db_session.add(new_order)
        db_session.commit()  # Committing order data

        # Creating order item
        new_order_item = OrderItems(
            orderID=orderID,
            productID=productID,
            quantity=quantityOrdered,
            unitPrice=unitPrice
        )
        db_session.add(new_order_item)
        db_session.commit()  # Committing order item data
        
        # Collecting order status
        paymentStatus = input("Enter Payment Status (Paid/Pending): ")
        orderStatus = input("Enter Order Status (Complete/Pending): ")
        shipmentDate = input("Enter Shipment Date: ")
        deliveryDate = input("Enter Delivery Date: ")
        notes = input("Enter Order Notes: ")
        
        order_status_table.add_row([
            orderID, paymentStatus, orderStatus, shipmentDate, deliveryDate, notes
        ])
        
        # Collecting return info
        returnRequested = input("Has a Return Been Requested? (Yes/No): ")
        returnApproved = input("Has the Return Been Approved? (Yes/No): ")
        refundProcessed = input("Has the Refund Been Processed? (Yes/No): ")
        reasonForReturn = input("Enter Reason for Return: ")
        
        refund_table.add_row([
            orderID, returnRequested, returnApproved, refundProcessed, reasonForReturn
        ])

# Get user input
get_user_input()

# Print tables
print(order_details_table)
print(product_details_table)
print(order_status_table)
print(refund_table)
