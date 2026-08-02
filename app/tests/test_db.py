from domain.repositories import db
import os
import sys
import unittest
from unittest.mock import MagicMock, patch

sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")))


class DbTests(unittest.TestCase):
    @patch.object(db, "init_db")
    @patch.object(db, "SessionLocal")
    def test_get_session_initializes_db_before_creating_session(
        self, mock_session_local, mock_init_db
    ):
        mocked_session = MagicMock()
        mock_session_local.return_value = mocked_session

        with db.get_session() as session:
            self.assertIs(session, mocked_session)

        mock_init_db.assert_called_once_with()
        mock_session_local.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
