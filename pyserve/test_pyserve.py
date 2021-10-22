
from __future__ import annotations

import random
import time
import unittest

from lib import Server, Address, Queue, FixedQueue, Client

class PyReturn(Server):
    def handle_request(self, addr: Address, data: dict):
        self.clients[addr].send(data)

class QueueTests(unittest.TestCase):

    def test_queue_unqueue_chain(self):
        q = Queue()
        for i in range(100):
            q.enqueue(i)
            self.assertEqual(i, q.dequeue())
    
    def test_queue_lots_unqueue_lots(self):
        q = Queue()
        for i in range(100):
            q.enqueue(i)
        for i in range(100):
            self.assertEqual(i, q.dequeue())

    def test_queue_overdequeue(self):
        q = Queue()
        for i in range(10):
            q.enqueue(i)
        for i in range(10):
            self.assertEqual(q.dequeue(), i)
        for i in range(10):
            self.assertIsNone(q.dequeue())

    def test_queue_massive_weird(self):
        q = Queue()
        for i in range(5000):
            q.enqueue(i)
        for i in range(3000):
            self.assertEqual(q.dequeue(), i)
        for i in range(2000):
            q.enqueue(i)
        for i in range(3000, 5000):
            self.assertEqual(i, q.dequeue())

class FixedQueueTests(unittest.TestCase):

    def test_collision_error(self):
        q = FixedQueue(96)
        with self.assertRaises(IndexError):
            for i in range(100):
                q.enqueue(i)

    def test_collision_error_tight(self):
        q = FixedQueue(4)
        with self.assertRaises(IndexError):
            for i in range(5):
                q.enqueue(i)
    
    def test_queue_lots_unqueue_lots(self):
        q = FixedQueue(100)
        for i in range(100):
            q.enqueue(i)
        for i in range(100):
            self.assertEqual(i, q.dequeue())

    def test_queue_overdequeue(self):
        q = FixedQueue(24)
        for i in range(10):
            q.enqueue(i)
        for i in range(10):
            self.assertEqual(q.dequeue(), i)
        for i in range(10):
            self.assertIsNone(q.dequeue())

    def test_queue_modulo(self):
        q = FixedQueue(96)
        for i in range(3000):
            q.enqueue(i)
            self.assertEqual(q.dequeue(), i)

class PyReturnTests(unittest.TestCase):

    def test_request(self):
        IP = Address("127.0.0.1", 31772)
        server = PyReturn(IP)
        server.operate()
        client = Client(IP)
        packet = {"127": 52}
        data = client.request(packet)
        self.assertEqual(data, packet)
        server.close()

    def test_requests(self):
        IP = Address("127.0.0.1", 31772)
        server = PyReturn(IP)
        server.operate()
        client = Client(IP)
        packet = {"127": 52}
        for i in range(10):
            data = client.request(packet)
            self.assertEqual(data, packet)
            packet["127"] += i
        server.close()

    def test_requests_diff(self):
        IP = Address("127.0.0.1", 31772)
        server = PyReturn(IP)
        with server.operate():
            client = Client(IP)
            packet = {"127": 52}
            for i in range(10):
                data = client.request(packet)
                self.assertEqual(data, packet)
                packet[f"127{i}"] = i ** 2

    def test_request_list(self):
        IP = Address("127.0.0.1", 31772)
        server = PyReturn(IP)
        with server.operate():
            client = Client(IP)
            packet = {"list": [_ for _ in range(900)]}
            self.assertEqual(packet, client.request(packet))

    def test_request_nested_dict(self):
        IP = Address("127.0.0.1", 31772)
        server = PyReturn(IP)
        with server.operate():
            client = Client(IP)
            packet = {"dict": {f"{i}": i + 5 for i in range(500)}}
            self.assertEqual(packet, client.request(packet))

    def test_large_request(self):
        IP = Address("127.0.0.1", 31772)
        server = PyReturn(IP)
        with server.operate():
            client = Client(IP)
            packet = {f"{i}": i + 0.5 for i in range(600)}
            data = client.request(packet)
            self.assertEqual(data, packet)

    def test_2x_client(self):
        IP = Address("127.0.0.1", 31772)
        server = PyReturn(IP)
        with server.operate():
            clients = [Client(IP) for _ in range(2)]
            for i in range(8):
                for client in clients:
                    self.assertEqual(client.request({"test": i}), {"test": i})

    def test_4x_client(self):
        IP = Address("127.0.0.1", 31772)
        server = PyReturn(IP)
        with server.operate():
            clients = [Client(IP) for _ in range(4)]
            for i in range(4):
                for client in clients:
                    self.assertEqual(client.request({"test": i}), {"test": i})

    def test_16x_client(self):
        IP = Address("127.0.0.1", 31772)
        server = PyReturn(IP)
        with server.operate():
            clients = [Client(IP) for _ in range(16)]
            for i in range(2):
                for client in clients:
                    self.assertEqual(client.request({"test": i}), {"test": i})

    def test_32x_random_client(self):
        IP = Address("127.0.0.1", 31772)
        server = PyReturn(IP)
        with server.operate():
            clients = [Client(IP) for _ in range(32)]
            for i in range(40):
                self.assertEqual(random.choice(clients).request({"test": i}), {"test": i})

    def test_32x_client_parallel(self):
        IP = Address("127.0.0.1", 31772)
        server = PyReturn(IP)
        with server.operate():
            clients = [Client(IP) for _ in range(32)]
            for i, client in enumerate(clients):
                client.send({"id": i})
            for i, client in enumerate(clients):
                self.assertEqual(client.recv(), {"id": i})

    def test_32x_client_parallel_random(self):
        IP = Address("127.0.0.1", 31772)
        server = PyReturn(IP)
        with server.operate():
            clients = [(Client(IP), i) for i in range(32)]
            random.shuffle(clients)
            for client, i in clients:
                client.send({"id": i})
            random.shuffle(clients)
            for client, i in clients:
                self.assertEqual(client.recv(), {"id": i})

    def test_128x_client_connect_disconnect(self):
        IP = Address("127.0.0.1", 31772)
        server = PyReturn(IP)
        with server.operate():
            clients = [Client(IP) for _ in range(128)]
            time.sleep(3.5) # it takes about 3 seconds for all of the clients to actually connect
            for client in clients:
                client.close()
            time.sleep(0.5)
        self.assertEqual(server.queue.read + server.queue.write, 256) # queue has been fully written to and full read
        # these two tests return 0 instead of previous 128 because correct PyReturn behaviour is to delete
        # stale connections
        self.assertEqual(sum((conn.closed for conn in server.clients.values())), 0) # checks all connections that are open
        self.assertEqual(sum((not conn.closed for conn in server.clients.values())), 0) # checks all connections that are closed


if __name__ == "__main__":
    unittest.main()
