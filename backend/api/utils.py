from django.http import HttpResponse


def dowload_shoppig_list(self, request, ingredients):
    response_content = "Список ингредиентов для покупоки:\n\n"
    for item in ingredients:
        ingredient_name = item["ingredient__name"]
        ingredient_measurement_unit = item["ingredient__measurement_unit"]
        ingredient_amount = item["total_amount"]
        response_content += (
            f'{ingredient_name}, '
            f'{ingredient_amount}'
            f'({ingredient_measurement_unit})\n'
        )
    response = HttpResponse(
        response_content,
        content_type='text/plain'
    )
    response['Content-Disposition'] = (
        'attachment; filename="shopping_cart.txt"'
    )
    return response
