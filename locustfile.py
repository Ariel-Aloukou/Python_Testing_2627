from locust import HttpUser, task, between


class GUDLFTUser(HttpUser):
    wait_time = between(1, 2)

    def on_start(self):
        """Simule la connexion d'un secrétaire"""
        self.client.post("/showSummary", data={"email": "john@simplylift.co"}, name="/showSummary (login)")

    @task(4)
    def view_competitions(self):
        """Consultation de la liste des compétitions"""
        self.client.post("/showSummary", data={"email": "john@simplylift.co"}, name="/showSummary")

    @task(3)
    def view_points_table(self):
        """Consultation du tableau public des points"""
        self.client.get("/points", name="/points")

    @task(2)
    def view_booking_page(self):
        """Accès à la page de réservation"""
        self.client.get("/book/Spring%20Festival/Simply%20Lift", name="/book/competition/club")

    @task(1)
    def purchase_places(self):
        """Achat de places"""
        self.client.post("/purchasePlaces", data={
            "competition": "Spring Festival",
            "club": "Simply Lift",
            "places": "1"
        }, name="/purchasePlaces")
