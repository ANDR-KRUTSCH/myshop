from django.test import TestCase
from django.db.models.query import QuerySet

from .models import Category, Product

# Create your tests here.
class PythonRecommenderTest(TestCase):
    
    class PythonRecommender:
        data_base = dict()
        
        def products_bought(self, products: list[Product]) -> None:
            products = [product.pk for product in products]

            for product in products:
                for with_product in products:
                    if product != with_product:
                        if product not in self.data_base:
                            details = self.data_base[product] = dict()
                            details[with_product] = 1
                        else:
                            details = self.data_base[product]
                            if with_product not in details:
                                details[with_product] = 1
                            else:
                                details[with_product] += 1

        def suggest_products_for(self, products: list[Product], max_results: int = 5) -> QuerySet:
            products = [product.pk for product in products]

            if len(products) == 1:
                with_products: dict = self.data_base[products[0]]
                suggestions = list(with_products.items())
            else:
                temp = self.data_base['temp'] = dict()
                for product in products:
                    details: dict = self.data_base[product]
                    for with_product in details.keys():
                        if with_product not in temp:
                            temp[with_product] = details[with_product]
                        else:
                            temp[with_product] += details[with_product]

                for product in products:
                    temp.pop(product)

                suggestions = list(temp.items())

                self.data_base.pop('temp')

            suggestions.sort(key=lambda item: item[1], reverse=True)
            suggestions = [product[0] for product in suggestions][:max_results]

            suggested_products = list(Product.objects.filter(pk__in=suggestions))

            suggested_products.sort(key=lambda x: suggestions.index(x.pk))

            return suggested_products
        
        def clear_purchases(self) -> None:
            for product in Product.objects.values_list('pk', flat=True):
                self.data_base.pop(product)


    def setUp(self) -> None:
        self.recommender = self.PythonRecommender()

    def test_suggest_products_for(self) -> None:
        category = Category.objects.create(name='Teas', slug='teas')

        green_tea = Product.objects.create(category=category, name='Green tea', slug='green-tea', price=0.9)
        black_tea = Product.objects.create(category=category, name='Black tea', slug='black-tea', price=1.9)
        red_tea = Product.objects.create(category=category, name='Red tea', slug='red-tea', price=2.9)
        tea_powder = Product.objects.create(category=category, name='Tea powder', slug='tea-powder', price=3.9)

        self.recommender.products_bought(products=[black_tea, red_tea])
        self.recommender.products_bought(products=[black_tea, green_tea])
        self.recommender.products_bought(products=[red_tea, black_tea, tea_powder])
        self.recommender.products_bought(products=[green_tea, tea_powder])
        self.recommender.products_bought(products=[black_tea, tea_powder])
        self.recommender.products_bought(products=[red_tea, green_tea])

        print(self.recommender.suggest_products_for(products=[black_tea]))
        print(self.recommender.suggest_products_for(products=[red_tea]))
        print(self.recommender.suggest_products_for(products=[green_tea]))
        print(self.recommender.suggest_products_for(products=[tea_powder]))

        print(self.recommender.suggest_products_for(products=[black_tea, red_tea]))
        print(self.recommender.suggest_products_for(products=[green_tea, red_tea]))
        print(self.recommender.suggest_products_for(products=[tea_powder, black_tea]))