from faststream.rabbit.fastapi import RabbitBroker, RabbitRouter

from ps.conf import RABBITMQ_URL

router = RabbitRouter(RABBITMQ_URL)
broker = RabbitBroker(RABBITMQ_URL)
