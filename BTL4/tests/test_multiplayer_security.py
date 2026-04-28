import socket
import time
import unittest

from scripts.multiplayer import HostActionResult, MultiplayerHost


class MultiplayerSecurityTest(unittest.TestCase):
    def make_host(self, capacity: int = 4) -> MultiplayerHost:
        return MultiplayerHost(
            host_name="Host",
            room_name="Security Test",
            password="",
            capacity=capacity,
            host_address="127.0.0.1",
        )

    def test_room_state_does_not_expose_player_tokens(self) -> None:
        host = self.make_host()
        try:
            room = host.room_state

            self.assertNotIn("token", room["players"][0])
            self.assertNotIn(host.host_player_token, str(room))
        finally:
            host.close()

    def test_join_uses_host_issued_token_not_client_supplied_token(self) -> None:
        host = self.make_host()
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            response, token = host._handle_join(
                {
                    "type": "join",
                    "room_id": host.room_id,
                    "player_name": "Guest",
                    "password": "",
                    "token": "client-controlled-token",
                },
                conn,
                ("127.0.0.1", 50000),
            )

            self.assertEqual(response["type"], "join_ok")
            self.assertIsNotNone(token)
            self.assertNotEqual(token, "client-controlled-token")
            self.assertEqual(response["token"], token)
            self.assertNotIn("client-controlled-token", str(response["room"]))
        finally:
            host.close()
            conn.close()

    def test_submit_action_uses_host_receive_time_not_client_time(self) -> None:
        host = self.make_host()
        captured_now_ms: list[int] = []

        def capture_validate(player_token: str, payload: dict, now_ms: int) -> HostActionResult:
            captured_now_ms.append(now_ms)
            return HostActionResult(True, "captured")

        host.validate_human_action = capture_validate  # type: ignore[method-assign]
        before_ms = int(time.time() * 1000)
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            response, returned_token = host._handle_client_message(
                {"type": "submit_action", "action": {"action_type": "draw"}, "now_ms": 1},
                conn,
                ("127.0.0.1", 50000),
                "joined-token",
            )
        finally:
            host.close()
            conn.close()

        self.assertEqual(returned_token, "joined-token")
        self.assertEqual(response, {"type": "action_ack", "ok": True, "message": "captured"})
        self.assertEqual(len(captured_now_ms), 1)
        self.assertGreaterEqual(captured_now_ms[0], before_ms)


if __name__ == "__main__":
    unittest.main()
