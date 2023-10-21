from rest_framework.response import Response
from rest_framework import viewsets, status
from .serializer import CurrencySerializer, CurrencySearchSerializer
from .models import CurrencyModel
from dotenv import load_dotenv
import redis
import requests
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
import json
import os

load_dotenv() 

redis_instance = redis.StrictRedis(
    host='localhost',
    port=6379,
    db=1
)

key = 'all_currencies'

class CurrencyViewSet(viewsets.ModelViewSet):
    serializer_class = CurrencySearchSerializer
    queryset = CurrencyModel.objects.all()

    def create(self, request):
        symbol = self.request.POST.get('symbol')
        symbol = symbol.upper()
        redis_data = redis_instance.get(symbol)

        if redis_data:
            data = json.loads(redis_data.decode('utf-8'))

            return Response(
                data,
                status = status.HTTP_200_OK
            )
        
        try:
            currency_model = CurrencyModel.objects.get(symbol=symbol)
            serialized_data = CurrencySerializer(currency_model).data
            redis_instance.setex(
                symbol,
                60,
                json.dumps(serialized_data)
            )

            return Response(
                serialized_data,
                status = status.HTTP_200_OK
            )
        
        except CurrencyModel.DoesNotExist:

            coinmarket_url = os.environ.get('COINMARKET_DOMAIN') + f"/v2/cryptocurrency/info?symbol={symbol}"
            api_key = os.environ.get('COINMARKET_API_KEY')

            headers = {
                'Accepts': 'application.json',
                'X-CMC_PRO_API_KEY': api_key
            }

            session = requests.Session()
            session.headers.update(headers)

            try:
                response = session.get(coinmarket_url)
                request_data = json.loads(response.text)

                if 'data' in request_data:
                    data = request_data['data'][symbol][0]

                    currencyModel = CurrencyModel(
                        name = data['name'],
                        symbol = symbol,
                        description = data['description'],
                        slug = data['slug']
                    )
                    
                    redis_instance.delete(key)
                    currencyModel.save()

                    serialized_data = CurrencySerializer(currencyModel).data

                    return Response(
                        serialized_data,
                        status = status.HTTP_201_CREATED    
                    )
                else:
                    return Response({
                        'error': 'No data found'
                    },
                    status = status.HTTP_400_BAD_REQUEST)
            except (ConnectionError, Timeout, TooManyRedirects) as e:
                return Response({
                    'error': 'ERROR PROCESSING THE REQUEST'
                },
                status = status.HTTP_INTERNAL_SERVER_ERROR)
    
    def list(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = CurrencySerializer(queryset, many=True)

        

        redis_data = redis_instance.get(key)
        
        if redis_data:
            data = json.loads(redis_data.decode('utf-8'))
            print("En redis cache")
            return Response(
                data,
                status = status.HTTP_200_OK
            )
        else:
            try:
                serializer = CurrencySerializer(queryset, many=True)
                data = serializer.data
                print("En database")
                redis_instance.setex(
                    key, 
                    60,
                    json.dumps(data)
                )
                
                return Response(
                    data,
                    status = status.HTTP_200_OK
                )
            except Exception as e:
                return Response({
                    'error': 'ERROR PROCESSING THE REQUEST',
                },
                status = status.HTTP_INTERNAL_SERVER_ERROR)