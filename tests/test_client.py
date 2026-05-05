from sppl import SavemaPrinterClient


class FakeTransport:
    def __init__(self, response=b"~SPGRES{SPPSTA:READY}^"):
        self.response = response
        self.opened = False
        self.closed = False
        self.sent = []

    def open(self):
        self.opened = True

    def close(self):
        self.closed = True

    def send(self, payload):
        self.sent.append(payload)

    def receive_until(self, terminator=b"^", max_bytes=65536):
        return self.response


def test_client_executes_command_with_transport():
    transport = FakeTransport()
    client = SavemaPrinterClient(transport)

    response = client.execute(client.get_printer_status())

    assert transport.sent == [b"~SPPSTA^"]
    assert response.source_command == "SPPSTA"
    assert response.values == ("READY",)


def test_client_context_manager_opens_and_closes_transport():
    transport = FakeTransport()

    with SavemaPrinterClient(transport) as client:
        assert client is not None
        assert transport.opened

    assert transport.closed

