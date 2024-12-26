from rest_framework.pagination import PageNumberPagination

from api.constant import PAGINATOR_PAGE_SIZE


class FoodgramPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    min_page_size = PAGINATOR_PAGE_SIZE
