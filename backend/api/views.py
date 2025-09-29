from django.shortcuts import render
from .models import Item
from .serializers import ItemSerializer
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.decorators import api_view
from rest_framework import status

@api_view(['GET'])
def testing_endpoint(request):
    return Response({
        'message': 'Hello from api',
        'status': 'success'
    })
@api_view(['GET'])
def items_list(request):
    items = Item.objects.all()
    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)

@api_view(['POST'])
def post_item(request):
    serializer = ItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



