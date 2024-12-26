from rest_framework.pagination import PageNumberPagination

from api.constant import MAX_PAGE_SIZE, PAGINATOR_PAGE_SIZE


class FoodgramPagination(PageNumberPagination):
    page_size_query_param = 'limit'
    page_size = PAGINATOR_PAGE_SIZE  # 6
    # max_page_size = MAX_PAGE_SIZE  # 10
