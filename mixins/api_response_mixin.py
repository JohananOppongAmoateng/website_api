from typing import Any, Optional, Union, List

from rest_framework import status
from rest_framework.pagination import PageNumberPagination
from rest_framework.request import Request
from rest_framework.response import Response


class APIResponseMixin:
    """
    A mixin to standardize API responses, providing both success and error response methods,
    including pagination support.
    """

    def success(
            self, message: str, data: Optional[Any] = None,
            status_code: int = status.HTTP_200_OK,
    ) -> Response:
        """
        Returns a standardized success response.

        :param message: A string message describing the success.
        :param data: Optional data to be included in the response.
        :param status_code: HTTP status code, default is 200 OK.
        :return: DRF Response object with standardized success format.
        """
        response_data = {
            "status": True,
            "message": message,
            "data": data
        }
        return Response(response_data, status=status_code)

    def error(
            self, message: str, errors: Optional[Union[str, List[str]]] = None,
            status_code: int = status.HTTP_400_BAD_REQUEST,
    ) -> Response:
        """
        Returns a standardized error response.

        :param message: A string message describing the error.
        :param errors: Optional error details can be a string or list of strings.
        :param status_code: HTTP status code, default is 400 BAD REQUEST.
        :return: DRF Response object with standardized error format.
        """
        response_data = {
            "status": False,
            "message": message,
            "errors": [errors] if isinstance(errors, str) else errors
        }
        return Response(response_data, status=status_code)

    def paginated_response(
            self, request: Request, queryset: Any, serializer_class: Any,
            message: str = "Success", page_size: int = 10,
            status_code: int = status.HTTP_200_OK,
    ) -> Response:
        """
        Returns a paginated response with next and previous URLs.

        :param request: The DRF request object.
        :param queryset: The queryset to paginate.
        :param serializer_class: The serializer class to use for the data.
        :param message: A string message describing the success.
        :param page_size: Number of items per page.
        :param status_code: HTTP status code, default is 200 OK.
        :return: DRF Response object with standardized pagination format.
        """
        paginator = PageNumberPagination()
        paginator.page_size = page_size

        if not queryset.ordered:
            queryset = queryset.order_by('created_at')

        paginated_queryset = paginator.paginate_queryset(queryset, request)

        data = serializer_class(paginated_queryset, many=True).data

        response_data = {
            "status": True,
            "message": message,
            "data": data,
            "status_code": status_code,
            "pagination": {
                "next": paginator.get_next_link(),
                "previous": paginator.get_previous_link(),
                "count": paginator.page.paginator.count,
                "current_page": paginator.page.number,
                "total_pages": paginator.page.paginator.num_pages
            }
        }
        return Response(response_data, status=status.HTTP_200_OK)
