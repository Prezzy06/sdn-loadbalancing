from prometheus_client import start_http_server
import time


def main() -> None:
    # Start Prometheus metrics for local dev (port 8000)
    start_http_server(8000)
    print("Metrics server started on :8000. Press Ctrl+C to exit.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()