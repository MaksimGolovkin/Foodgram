from rest_framework.pagination import PageNumberPagination

from api.constant import PAGE_SIZE, PAGINATOR_PAGE_SIZE


class FoodgramPagination(PageNumberPagination):
    page_size = PAGINATOR_PAGE_SIZE
    page_size_query_param = 'limit'
    max_page_size = PAGE_SIZE
