from src.helpers import generate_secrets, get_redis


def test_generate_secrets_len():
    assert len(generate_secrets(10)) == 10


def test_generate_secrets_valid():
    secrets = generate_secrets(10)
    r = get_redis()
    for secret in secrets:
        value = r.get(f"token_{secret}")
        assert value == b"0"


def test_generate_secrets_number():
    r = get_redis()
    existing_secrets = []
    for key in r.scan_iter("token_*"):
        value = r.get(key)
        if value == b"0":
            existing_secrets.append(key[6:].decode("utf-8"))
    secrets = generate_secrets(10)
    assert len(set(existing_secrets).intersection(secrets)) == len(existing_secrets)
