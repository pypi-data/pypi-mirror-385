from rnet.blocking import Client


def main():
    client = Client()
    resp = client.post(
        "https://httpbin.org/anything",
        form=[("key", "value")],
    )
    print(resp.text())


if __name__ == "__main__":
    main()
