from setuptools import setup, find_packages

setup(
    name="aescryptox",
    version="0.0.1",
    author="ATHALLAH RAJENDRA PUTRA JUNIARTO",
    author_email="youremail@example.com",
    description="Pure Python AES encryption library supporting ECB, CBC, PCBC, CTR, GCM, CCM, XTS, SIV, EAX, OCB3, OFB, CFB, with file encryption and HMAC.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/Athallah1234/AESCryptoX",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Topic :: Security :: Cryptography",
    ],
    python_requires=">=3.7",
)
