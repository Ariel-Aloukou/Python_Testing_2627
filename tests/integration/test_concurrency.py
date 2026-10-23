import threading
import time

import server


def test_concurrent_purchases_are_serialized(app, monkeypatch):
    original_save_data = server.saveData
    active = 0
    max_active = 0
    counter_lock = threading.Lock()

    def slow_save_data():
        nonlocal active, max_active
        with counter_lock:
            active += 1
            max_active = max(max_active, active)
        time.sleep(0.05)
        original_save_data()
        with counter_lock:
            active -= 1

    monkeypatch.setattr(server, "saveData", slow_save_data)

    start = threading.Barrier(2)

    def purchase(email, places):
        client = app.test_client()
        client.post(
            "/showSummary",
            data={"email": email},
        )
        start.wait()
        client.post(
            "/purchasePlaces",
            data={
                "competition": "Small Festival",
                "places": places,
            },
        )

    threads = [
        threading.Thread(
            target=purchase,
            args=("john@simplylift.co", "3"),
        ),
        threading.Thread(
            target=purchase,
            args=("admin@irontemple.com", "3"),
        ),
    ]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert max_active == 1
    booked_places = (
        server.get_booked_places("Simply Lift", "Small Festival")
        + server.get_booked_places("Iron Temple", "Small Festival")
    )
    assert booked_places == 3
    assert server.competitions[2]["numberOfPlaces"] == 2
