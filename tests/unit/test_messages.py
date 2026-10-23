from flask import get_flashed_messages

import server


def test_flash_error_uses_error_category(app):
    with app.test_request_context("/"):
        server.flash_error("Erreur de test")

        assert get_flashed_messages(with_categories=True) == [
            ("error", "Erreur de test")
        ]


def test_flash_success_uses_success_category(app):
    with app.test_request_context("/"):
        server.flash_success("Réservation réussie")

        assert get_flashed_messages(with_categories=True) == [
            ("success", "Réservation réussie")
        ]
