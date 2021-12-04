import base64

import httpx
import pytest
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import PlainTextResponse, Response

snapshot_apt_Release = """
Origin: . stable
Label: . stable
Suite: stable
Codename: stable
Date: Thu, 11 Nov 2021 05:22:02 UTC
Architectures: amd64
Components: devops secops
Description: Generated by aptly
"""

snapshot_apt_devops_binary_amd64_Packages = """
Package: kube-score
Priority: optional
Section: python
Installed-Size: 18315
Maintainer: ops2deb <ops2deb@upciti.com>
Architecture: amd64
Version: 1.12.0-1~ops2deb
Filename: pool/devops/k/kube-score/kube-score_1.12.0-1~ops2deb_amd64.deb
Size: 3922220
MD5sum: a016569e433f172fa177487f7dab444b
SHA1: f0e3c72da12bf03fa7a864ef4c4694abe53c64f2
SHA256: 6be2a102643da0b5d1f4ccfc1888fc06b1dcf4836fdd6d50a59af0c012c2f4b7
SHA512: 84b3405fbb1924d19ce5cdf1807cf87b231f4045f5978082f05cb0811b795ac8276a8d8374568acc9ec23a56b7571e02328072a65a0dd8345a1b8c6575d7e783
Description: Kubernetes object analysis with recommendations for improved reliability and security.
  kube-score is a tool that performs static code analysis of
  your Kubernetes object definitions.
"""

snapshot_apt_secops_binary_amd64_Packages = """
Package: great-app
Priority: optional
Section: python
Installed-Size: 38226
Maintainer: ops2deb <ops2deb@upciti.com>
Architecture: all
Version: 1.0.0-1~ops2deb
Filename: pool/secops/g/great-app/great-app_1.0.0-1~ops2deb_all.deb
Size: 9511932
MD5sum: 9a8bb37b97b3e235f24d6a863c72dfa2
SHA1: e3e49a07cccb660b8f5f4419ac982d10724b0ff6
SHA256: 0898efd0c85c6c66e028b88442d2e8f1d75ef3d0d487e2b2d545a43ac2e8134e
SHA512: d835b92cee91b48e308cd5a47502f0743174c1aafd026a30718e93bf92344ad56e3cd02ae0e8e47bbde719eeaf5f4bd10a873966f81347de0c80dce8cf73e5a7
Description: Great package
  A detailed description of the great package

Package: super-app
Priority: optional
Section: python
Installed-Size: 131575
Maintainer: ops2deb <ops2deb@upciti.com>
Architecture: all
Version: 1.0.0-1~ops2deb
Filename: pool/secops/s/super-app/super-app_1.0.0-1~ops2deb_amd64.deb
Size: 25678524
MD5sum: 62f729a690646275abdc8c5414f2aa02
SHA1: 7b3fc5a1ae0dbc18f9abb3293d12689c4e59ad33
SHA256: 11be2fa0f0d63469a5b4f9c296f77dac69d98441c8c84f9544eb66bd8832d39f
SHA512: 7cc122b9406f52f6bd0955eff05b1efd17ba104c598953ba7000b23f63df1419aa4c7f6ce790cf193263f693a617050f20a38decc216027fda93007659b2020d
Description: Super package
  A detailed description of the super package
"""

starlette_app = Starlette(debug=True)


@starlette_app.route("/dists/stable/Release")
async def serve_snapshot_apt_release(request: Request):
    return PlainTextResponse(content=snapshot_apt_Release)


@starlette_app.route("/dists/stable/devops/binary-amd64/Packages")
async def serve_snapshot_apt_devops_binary_amd64_packages(request: Request):
    return PlainTextResponse(content=snapshot_apt_devops_binary_amd64_Packages)


@starlette_app.route("/dists/stable/secops/binary-amd64/Packages")
async def serve_snapshot_apt_secops_binary_amd64_packages(request: Request):
    return PlainTextResponse(content=snapshot_apt_secops_binary_amd64_Packages)


@starlette_app.route("/1.0.0/great-app.tar.gz")
@starlette_app.route("/1.1.0/great-app.tar.gz")
@starlette_app.route("/1.1.1/great-app.tar.gz")
async def server_great_app__tar_gz(request: Request):
    # b64 encoded tar.gz with an empty "great-app" file
    dummy_tar_gz_file = (
        b"H4sIAAAAAAAAA+3OMQ7CMBAEQD/FH0CyjSy/xwVCFJAoCf/HFCAqqEI1U9yudF"
        b"fceTn17dDnOewnDa3VZ+ZW02e+hHxsrYxRagkp59FDTDv+9HZft77EGNbLdbp9uf"
        b"u1BwAAAAAAAAAAgD96AGPmdYsAKAAA"
    )
    return Response(
        base64.b64decode(dummy_tar_gz_file),
        status_code=200,
        media_type="application/x-gzip",
    )


@starlette_app.route("/1.0.0/super-app.zip")
async def serve_super_app_zip(request: Request):
    dummy_zip_file = (
        b"UEsDBBQACAAIAFVdkFIAAAAAAAAAAAAAAAAJACAAZ3JlYXQtYXBwVVQNAAcTXHlgE1x5YBNceWB1"
        b"eAsAAQToAwAABOgDAAADAFBLBwgAAAAAAgAAAAAAAABQSwECFAMUAAgACABVXZBSAAAAAAIAAAAA"
        b"AAAACQAgAAAAAAAAAAAAtIEAAAAAZ3JlYXQtYXBwVVQNAAcTXHlgE1x5YBNceWB1eAsAAQToAwAA"
        b"BOgDAABQSwUGAAAAAAEAAQBXAAAAWQAAAAAA"
    )
    return Response(
        base64.b64decode(dummy_zip_file),
        status_code=200,
        media_type="application/zip",
    )


@starlette_app.route("/1.1.0/bad-app.zip")
async def serve_error_500(request: Request):
    return Response(status_code=500)


@pytest.fixture(scope="function")
def mock_httpx_client():
    real_async_client = httpx.AsyncClient

    def async_client_mock(**kwargs):
        kwargs.pop("transport", None)
        return real_async_client(app=starlette_app, **kwargs)

    httpx.AsyncClient = async_client_mock
    yield
    httpx.AsyncClient = real_async_client
