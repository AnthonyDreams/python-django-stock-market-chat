from celery import shared_task
from .services.Stock import StockService, InvalidStock
import re
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()


@shared_task
def run_stock_bot(consumer_context):
    try:
        stock_code = stock_code = re.search(
            '(?<==)([^\s]+)', consumer_context['message']).group(0).strip()
        message = StockService().getStock(stock_code)

        async_to_sync(channel_layer.group_send)(
            consumer_context.pop('group'),
            {
                **consumer_context,
                "user":"bot",
                "message": message
            }
        )
    except InvalidStock:
        async_to_sync(channel_layer.send)(
            consumer_context.pop('own_channel'),
            {
                **consumer_context,
                "user":"bot",
                "message": "Invalid Symbol"
            }
        )

    except:
        async_to_sync(channel_layer.send)(
            consumer_context.pop('own_channel'),
            {
                **consumer_context,
                "user":"bot",
                "message": "There was a error with the stock market bot"
            }
        )
