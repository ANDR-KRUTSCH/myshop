import redis

from django.db.models.query import QuerySet
from django.conf import settings

from .models import Product

my_redis = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


class Recommender:

    def get_product_key(self, product_pk) -> str:
        return f'product:{product_pk}:purchased_with'
    
    def products_bought(self, products: list[Product]) -> None:
        product_pks = [product.pk for product in products]

        for product_pk in product_pks:
            for with_pk in product_pks:
                if product_pk != with_pk:
                    my_redis.zincrby(name=self.get_product_key(product_pk=product_pk), amount=1, value=with_pk)

    def suggest_products_for(self, products: list[Product], max_results: int = 5) -> QuerySet:
        product_pks = [product.pk for product in products]

        if len(product_pks) == 1:
            suggestions = my_redis.zrange(name=self.get_product_key(product_pk=product_pks[0]), start=0, end=-1, desc=True)[:max_results]
        else:
            flat_ids = ''.join([str(product_pk) for product_pk in product_pks])
            tmp_key = f'tmp_{flat_ids}'
            keys = [self.get_product_key(product_pk=product_pk) for product_pk in product_pks]
            my_redis.zunionstore(dest=tmp_key, keys=keys)
            my_redis.zrem(tmp_key, *product_pks)
            suggestions = my_redis.zrange(name=tmp_key, start=0, end=-1, desc=True)[:max_results]
            my_redis.delete(tmp_key)
        suggested_products_pks = [int(product_pk) for product_pk in suggestions]
        suggested_products = list(Product.objects.filter(pk__in=suggested_products_pks))
        suggested_products.sort(key=lambda x: suggested_products_pks.index(x.pk))
        return suggested_products
    
    def clear_purchases(self) -> None:
        for product_pk in Product.objects.values_list('pk', flat=True):
            my_redis.delete(self.get_product_key(product_pk=product_pk))