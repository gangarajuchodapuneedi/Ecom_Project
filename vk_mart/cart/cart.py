# class Cart:
#     def __init__(self):
#         self.items = []

#     def add_item(self, item):
#         self.items.append(item)

#     def remove_item(self, item):
#         self.items.remove(item)

#     def get_items(self):
#         return self.items

class Cart:
    def __init__(self, request):
        """Initialize the cart"""
        self.session = request.session
        cart = self.session.get("cart")
        if not cart or not isinstance(cart, dict):  # Ensure cart is a dictionary
            cart = self.session["cart"] = {}
        self.cart = cart

    def add_item(self, product,extra_data=None):
        """Add an item to the cart"""
        product_id = str(product.id)  # Convert ID to string for JSON storage
         # Debugging print statements
        # Ensure the image URL is stored correctly
        image_url = product.featured_image.strip() if product.featured_image else ""

        print(f"DEBUG: Adding Product - ID: {product.id}, Name: {product.product_name}, Image URL: {image_url}")

        # Ensure the product data is stored as a dictionary
        if product_id in self.cart and isinstance(self.cart[product_id], dict):
            self.cart[product_id]["quantity"] += 1
        else:
            self.cart[product_id] = {
                "product_name": product.product_name,
                "quantity": 1,
                "price": extra_data.get("discounted_price", product.price),
                "packing_cost": product.packing_cost,
                "tax": product.tax,
                "featured_image": image_url
            }
        # Debugging print statements after adding item
        print(f"Cart Data After Adding: {self.cart}")

        self.session["cart"] = self.cart  # Update session
        self.session.modified = True  # Mark session as updated

    def decrement_item(self, product):
                """Decrement the quantity of an item in the cart"""
                product_id = str(product.id)

                if product_id in self.cart and isinstance(self.cart[product_id], dict):
                    if self.cart[product_id]["quantity"] > 1:
                        self.cart[product_id]["quantity"] -= 1
                    else:
                        del self.cart[product_id]  # Remove item if quantity reaches 0
                
                self.session["cart"] = self.cart  # Update session
                self.session.modified = True


    def remove(self, product_id):
        """Remove an item from the cart"""
        product_id = str(product_id)
        if product_id in self.cart:
            del self.cart[product_id]
            self.session["cart"] = self.cart  # Update session
            self.session.modified = True

    def get_items(self):
        """Return all items in the cart"""
        return self.cart
    
    def clear(self):
        """Clear all items from the cart."""
        self.session["cart"] = {}
        self.session.modified = True
