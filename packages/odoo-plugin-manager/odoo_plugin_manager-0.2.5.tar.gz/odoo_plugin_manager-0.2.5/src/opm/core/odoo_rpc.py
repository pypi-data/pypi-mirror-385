from __future__ import annotations
import xmlrpc.client

class OdooRPC:
    def __init__(self, url: str, db: str, user: str, password: str):
        self.url = url.rstrip("/")
        self.db = db
        self.user = user
        self.password = password
        self.uid = None
        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common")
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object")

    def login(self):
        self.uid = self.common.authenticate(self.db, self.user, self.password, {})
        if not self.uid:
            raise RuntimeError("Odoo login failed")

    def call(self, model: str, method: str, *args, **kwargs):
        if not self.uid:
            self.login()
        return self.models.execute_kw(self.db, self.uid, self.password, model, method, list(args), kwargs)