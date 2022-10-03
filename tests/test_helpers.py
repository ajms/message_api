from src.helpers import generate_secrets, get_redis


def test_generate_secrets_len():
    assert len(generate_secrets(10)) == 10


def test_generate_secrets_valid():
    secrets = generate_secrets(10)
    r = get_redis()
    for secret in secrets:
        value = r.hget("secret", secret)
        assert value == b"unused secret"


def test_generate_secrets_number():
    r = get_redis()
    existing_secrets = []
    for key, used_flag in r.hscan_iter("secret", "*"):
        if used_flag == b"unused secret":
            existing_secrets.append(key.decode("utf-8"))
    secrets = generate_secrets(10)
    assert len(set(existing_secrets).intersection(secrets)) == len(existing_secrets)
