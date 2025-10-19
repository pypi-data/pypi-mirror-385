import unittest
from unittest.mock import Mock, patch
from zentropy import Client, AuthError

class TestClient(unittest.TestCase):
    
    @patch('zentropy.client.Connection')
    def test_auth_success(self, mock_conn):
        mock_conn.return_value.recv.return_value = b'OK'
        client = Client(password='testpass')
        self.assertTrue(client.auth('testpass'))
    
    @patch('zentropy.client.Connection')
    def test_auth_failure(self, mock_conn):
        mock_conn.return_value.recv.return_value = b'ERROR'
        with self.assertRaises(AuthError):
            Client(password='wrongpass')
    
    @patch('zentropy.client.Connection')
    def test_set_get(self, mock_conn_class):
        mock_conn = Mock()
        mock_conn_class.return_value = mock_conn
        mock_conn.recv.side_effect = [b'OK', b'value']
        
        client = Client()
        self.assertTrue(client.set('key', 'value'))
        self.assertEqual(client.get('key'), 'value')

if __name__ == '__main__':
    unittest.main()