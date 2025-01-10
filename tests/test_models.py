# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(name="Fedora", description="A red hat", price=12.50, available=True, category=Category.CLOTHS)
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    def test_read_a_product(self):
        """Test function to read a product"""
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id
        self.assertIsNotNone(product.id)
        # Fetch product from Database
        found_product = Product.find(product.id)
        # Assert matching properties such as id, name, description, price
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)

    def test_update_a_product(self):
        """Test function to update a Product"""
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id
        self.assertIsNotNone(product.id)
        # Change product description
        description = "New description"
        product.description = description
        original_id = product.id
        product.update()
        self.assertEqual(product.id, original_id)
        self.assertEqual(product.description, description)
        # Fetch all product and check updates
        products_all = Product.all()
        self.assertEqual(len(products_all), 1)
        self.assertEqual(products_all[0].id, original_id)
        self.assertEqual(products_all[0].description, description)
        # Test error thrown when updating a product with empty description
        product.id = None
        with self.assertRaises(Exception):
            product.update()

    def test_delete_a_product(self):
        """Test function to delete a Product"""
        product = ProductFactory()
        product.create()
        # Assert there is only a single product in the database
        self.assertEqual(len(Product.all()), 1)
        # Delete product and assert there is 0 products in db
        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """Test function to list all Products in database"""
        products = Product.all()
        # Assert there are no products in database
        self.assertEqual(products, [])
        # Create 5 products
        for _ in range(5):
            product = ProductFactory()
            product.create()
        # Assert there are 5 products in database
        products = Product.all()
        self.assertEqual(len(products), 5)

    def test_find_by_name(self):
        """Test function to find a product by name"""
        # Create 5 products
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        # Name of first product
        name = products[0].name
        # Check how many products have the same name
        count = len([product for product in products if product.name == name])
        # Use the name to retrieve from database
        found = Product.find_by_name(name)
        # Assert nb. of product with same name is equal to nb. of products
        # retrieved from database
        self.assertEqual(found.count(), count)
        # Assert name of retrieved products is same
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_price(self):
        """Test function to find a product by price"""
        # Create 10 products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Price of first product
        price = products[0].price
        # Check how many products have the same price
        count = len([product for product in products if product.price == price])
        # Retrieve products with same price
        found = Product.find_by_price(price)
        # Assert nb. of product with same price is equal to nb. of products
        # retrieved from database
        self.assertEqual(found.count(), count)
        # Assert price of retrieved products is same
        for product in found:
            self.assertEqual(product.price, price)

    def test_find_by_availability(self):
        """Test function to find a product by availability"""
        # Create 10 products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Availability of first product
        available = products[0].available
        # Check how many products have the same availability
        count = len([product for product in products if product.available == available])
        # Retrieve products with same availability
        found = Product.find_by_availability(available)
        # Assert nb. of product with same availability is equal to nb. of products
        # retrieved from database
        self.assertEqual(found.count(), count)
        # Assert availability of retrieved products is same
        for product in found:
            self.assertEqual(product.available, available)

    def test_find_by_category(self):
        """Test function to find a product by category"""
        # Create 10 products
        products = ProductFactory.create_batch(10)
        for product in products:
            product.create()
        # Category of first product
        category = products[0].category
        # Check how many products have the same category
        count = len([product for product in products if product.category == category])
        # Retrieve products with same category
        found = Product.find_by_category(category)
        # Assert nb. of product with same category is equal to nb. of products
        # retrieved from database
        self.assertEqual(found.count(), count)
        # Assert category of retrieved products is same
        for product in found:
            self.assertEqual(product.category, category)
