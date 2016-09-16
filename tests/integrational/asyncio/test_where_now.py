import asyncio
import pytest

from pubnub.pubnub_asyncio import PubNubAsyncio, SubscribeListener
from tests.helper import pnconf_sub_copy
from tests.integrational.vcr_asyncio_sleeper import get_sleeper
from tests.integrational.vcr_helper import pn_vcr


@get_sleeper('tests/integrational/fixtures/asyncio/where_now/single_channel.yaml')
@pn_vcr.use_cassette(
    'tests/integrational/fixtures/asyncio/where_now/single_channel.yaml',
    filter_query_parameters=['uuid'])
@pytest.mark.asyncio
def test_single_channel(event_loop, sleeper=asyncio.sleep):
    pubnub = PubNubAsyncio(pnconf_sub_copy(), custom_event_loop=event_loop)
    ch = 'test-where-now-asyncio-ch'
    uuid = 'test-where-now-asyncio-uuid'
    pubnub.config.uuid = uuid

    callback = SubscribeListener()
    pubnub.add_listener(callback)
    pubnub.subscribe().channels(ch).execute()

    yield from callback.wait_for_connect()

    yield from sleeper(2)

    env = yield from pubnub.where_now() \
        .uuid(uuid) \
        .future()

    channels = env.result.channels

    assert len(channels) == 1
    assert channels[0] == ch

    pubnub.unsubscribe().channels(ch).execute()
    yield from callback.wait_for_disconnect()

    pubnub.stop()


@get_sleeper('tests/integrational/fixtures/asyncio/where_now/multiple_channels.yaml')
@pn_vcr.use_cassette(
    'tests/integrational/fixtures/asyncio/where_now/multiple_channels.yaml',
    match_on=['method', 'scheme', 'host', 'port', 'string_list_in_path', 'query'],
    match_on_kwargs={
        'string_list_in_path': {
            'positions': [4]
        }
    })
@pytest.mark.asyncio
def test_multiple_channels(event_loop, sleeper=asyncio.sleep):
    pubnub = PubNubAsyncio(pnconf_sub_copy(), custom_event_loop=event_loop)

    ch1 = 'test-where-now-asyncio-ch1'
    ch2 = 'test-where-now-asyncio-ch2'
    uuid = 'test-where-now-asyncio-uuid'
    pubnub.config.uuid = uuid

    callback = SubscribeListener()
    pubnub.add_listener(callback)
    pubnub.subscribe().channels([ch1, ch2]).execute()

    yield from callback.wait_for_connect()

    yield from sleeper(7)

    env = yield from pubnub.where_now() \
        .uuid(uuid) \
        .future()

    channels = env.result.channels

    assert len(channels) == 2
    assert ch1 in channels
    assert ch2 in channels

    pubnub.unsubscribe().channels([ch1, ch2]).execute()
    yield from callback.wait_for_disconnect()

    pubnub.stop()