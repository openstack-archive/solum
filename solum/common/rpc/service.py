# Copyright 2014 - Rackspace Hosting
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

"""Common RPC service and API tools for Solum."""

import eventlet
from oslo_config import cfg
import oslo_messaging as messaging
from oslo_messaging.rpc import dispatcher
from oslo_serialization import jsonutils

import solum.common.context
from solum import objects


# NOTE(paulczar):
# Ubuntu 14.04 forces librabbitmq when kombu is used
# Unfortunately it forces a version that has a crash
# bug.  Calling eventlet.monkey_patch() tells kombu
# to use libamqp instead.
eventlet.monkey_patch()


class JsonPayloadSerializer(messaging.NoOpSerializer):
    @staticmethod
    def serialize_entity(context, entity):
        return jsonutils.to_primitive(entity, convert_instances=True)


class RequestContextSerializer(messaging.Serializer):

    def __init__(self, base=None):
        self._base = base or messaging.NoOpSerializer()

    def serialize_entity(self, context, entity):
        if not self._base:
            return entity
        return self._base.serialize_entity(context, entity)

    def deserialize_entity(self, context, entity):
        if not self._base:
            return entity
        return self._base.deserialize_entity(context, entity)

    def serialize_context(self, context):
        return context.to_dict()

    def deserialize_context(self, context):
        return solum.common.context.RequestContext.from_dict(context)


class Service(object):
    _server = None

    def __init__(self, topic, server, handlers):
        serializer = RequestContextSerializer(JsonPayloadSerializer())
        transport = messaging.get_notification_transport(cfg.CONF)
        # TODO(asalkeld) add support for version='x.y'
        target = messaging.Target(topic=topic, server=server)
        access_policy = dispatcher.DefaultRPCAccessPolicy
        self._server = messaging.get_rpc_server(transport, target, handlers,
                                                serializer=serializer,
                                                access_policy=access_policy)

    def serve(self):
        objects.load()
        self._server.start()
        self._server.wait()


class API(object):
    def __init__(self, transport=None, context=None, topic=None):
        serializer = RequestContextSerializer(JsonPayloadSerializer())
        if transport is None:
            transport = messaging.get_notification_transport(cfg.CONF)
        self._context = context
        if topic is None:
            topic = ''
        target = messaging.Target(topic=topic)
        self._client = messaging.RPCClient(transport, target,
                                           serializer=serializer)

    def _call(self, method, *args, **kwargs):
        return self._client.call(self._context, method, *args, **kwargs)

    def _cast(self, method, *args, **kwargs):
        self._client.cast(self._context, method, *args, **kwargs)

    def echo(self, message):
        self._cast('echo', message=message)
