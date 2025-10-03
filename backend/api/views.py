from django.shortcuts import render
from .models import Item
from .serializers import ItemSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import status

"""
This is a test endpoint, nothing useful
"""
@api_view(['GET'])
def testing_endpoint(request):
    return Response({
        'message': 'Hello from api',
        'status': 'success'
    })

"""
Get list of items
"""
@api_view(['GET'])
def items_list(request):
    items = Item.objects.all()
    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)

"""
Create a new item
"""
@api_view(['POST'])
def post_item(request):
    serializer = ItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""
Operations on a single selected item
"""
@api_view(['GET', 'PUT', 'DELETE'])
def item_details(request, pk):
    try:
        item = Item.objects.get(pk=pk)
    except Item.DoesNotExist:
        return Response(
            {'error': 'Item does not exist'},
            status = status.HTTP_400_BAD_REQUEST
        )
    if request.method == 'GET':
        serializer = ItemSerializer(item)
        return Response(serializer.data)
    elif request.method == 'PUT':
        serializer = ItemSerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    






