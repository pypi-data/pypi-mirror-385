
import os
from envencrypt.main import load_dotenve


def main():
    load_dotenve(encrypt_in_background=False, encrypt_override=True)
    print(os.environ["SECRET"])
    print(os.environ["DOMAIN"])
    print(os.environ["ADDITIONAL"])
    print("done")


if __name__ == "__main__":
    main()