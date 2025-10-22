#!/usr/bin/env python3


def name() -> str:
    """
    Provides my full name.

    :return: My full name
    :rtype: str
    """
    return "Samuel Mehalko"


def title() -> str:
    """
    Provides my title at the company that I am employeed.

    :return: My title
    :rtype: str
    """
    return "Senior Principle Embedded Software Engineer"


def company() -> str:
    """
    Provides the name of the company that I am employeed.

    :return: My company
    :rtype: str
    """
    return "Northrop Grumman Corporation"


def email() -> str:
    """
    Provides my office email address.

    :return: My email address
    :rtype: str
    """
    return "samuel.mehalko@ngc.com"


def site() -> str:
    """
    Provides the url of readthedocs website for this repo.

    :return: The readthedocs url
    :rtype: str
    """
    return "https://meetsam.readthedocs.io"


def source() -> str:
    """
    Provides the url of the this package's source github url.

    :return: This source code's github url.
    :rtype: str
    """
    return "https://github.com/SamuelDonovan/meetSam"


def installation() -> str:
    """
    Provides the pip installation command for meetSam. 

    :return: The pip installation command for meetSam. 
    :rtype: str
    """
    return "pip install meetSam"


def qr_code() -> str:
    """
    Provides a QR code for the website URL.

    :return: The QR code. 
    :rtype: str
    """
    return """
    █▀▀▀▀▀█ █▄█ ▄▀█   █▀▀▀▀▀█
    █ ███ █  █ █▀█▄ █ █ ███ █
    █ ▀▀▀ █ █▄█  ▀▀   █ ▀▀▀ █
    ▀▀▀▀▀▀▀ █ █▄█ █▄█ ▀▀▀▀▀▀▀
    ███  █▀▄▀█▀▄▀  ▄▀▀██▀▄ ██
     █    ▀▄█▄ █ ▀ ▀▄▄▀▄██▀ ▀
    ▀▀  ▀█▀▄ ▀ █▄ ▄▄█ ██   ▄█
    ▀▀ ▄▄ ▀▄▀  █ ▀ ▀ ▄▀▄▄█▀ ▀
    ▀▀▀▀▀▀▀▀▄▄ ██▄ ▀█▀▀▀█  ▀▄
    █▀▀▀▀▀█ ▄█ █▄▀▀▄█ ▀ █  ▄█
    █ ███ █  ▄█▄█  ███▀▀█ ▄▄ 
    █ ▀▀▀ █ █▄▀▀█▀▄██▄ ██▀ ▀▀
    ▀▀▀▀▀▀▀ ▀▀ ▀▀   ▀▀▀  ▀  ▀
    """


def main() -> str:
    """
    Provides a short blurb of of my contact information as well as some fun links.

    :return: My contact information as well as some fun links.
    :rtype: str
    """
    print(
        f"""
    Hi, my name is {name()}!
    I am a {title()}
    working for {company()}.
    I can be reached via email at {email()}

    The python package used to generate this text can be found at {site()}
    and the source can be found at {source()}

    QR code to site:
    {qr_code()}
    """
    )


if __name__ == "__main__":
    main()
