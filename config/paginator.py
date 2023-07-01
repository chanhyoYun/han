from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.utils.urls import remove_query_param


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link(),
                },
                "count": self.page.paginator.count,
                "results": data,
            }
        )

    def get_next_link(self):
        if not self.page.has_next():
            return None
        page_number = self.page.next_page_number()
        # url = "http://127.0.0.1:8000/users/ranking/"
        url = "https://backend.barryjung.com/users/ranking/"
        if self.request.query_params.get("type") == "battle":
            return f"{url}?type=battle&page={page_number}"
        return f"{url}?page={page_number}"

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        page_number = self.page.previous_page_number()
        # url = "http://127.0.0.1:8000/users/ranking/"
        url = "https://backend.barryjung.com/users/ranking/"
        if self.request.query_params.get("type") == "battle":
            return f"{url}?type=battle&page={page_number}"
        if page_number == 1:
            if self.request.query_params.get("type") == "battle":
                return remove_query_param(url, self.page_query_param) + "?type=battle"
            return remove_query_param(url, self.page_query_param)
        return f"{url}?page={page_number}"
