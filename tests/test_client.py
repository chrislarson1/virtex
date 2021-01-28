# -------------------------------------------------------------
# Copyright 2021 Virtex authors. All Rights Reserved.
# -------------------------------------------------------------


# async def send_spam(url, messages, client):
#     tasks = []
#     for msg in messages:
#         tasks.append(asyncio.ensure_future(client.post_async(url, msg)))
#     return await asyncio.gather(*tasks)
#
#
# def test_client_embedding_async(tweets):
#     messages = [HttpMessage(data=tweets) for _ in range(N)]
#     tasks = []
#     t = time.time()
#     fut = asyncio.ensure_future(send_spam(url, messages))
#     responses = loop.run_until_complete(fut)
#     t = time.time() - t
#     ex = responses[0]
#     ex.decode(decode_np)
#     print("    RECEIVED DTYPE: %s" % type(ex.data[0]))
#     print("SERVER PERFORMANCE: %d TPS" % int((len(text_data) * N) / t))
#
#
# def test_client_embedding():
#     message = HttpMessage(data=text_data)
#     response = client.post(url, message)
#     response.decode(decode_np)
#     print("RECEIVED DTYPE: %s" % type(response.data[0]))


# if __name__ == '__main__':
#     N = 1000
#     url = 'http://127.0.0.1:8081'
#     loop = asyncio.get_event_loop()
#     client = Client(loop=loop)
#     test_client_embedding()
    # test_client_embedding_async()
