from http.client import HTTPException, NOT_FOUND
import argparse
import re
from typing import TypeAlias, Any, Optional
from dataclasses import dataclass, field
import http.client
import json


def arg_parser():
    parser = argparse.ArgumentParser(description="Simple release getter")
    parser.add_argument('--version', default="latest", help="Pick a release version")
    return parser.parse_args()



@dataclass
class Github:
    domain: str = "api.github.com"
    _release_path: str = "/repos/plantuml/plantuml/releases"
    regex: str = r".*plantuml.*?\d+\.\d+\.jar$"
    version: str = "latest"

    @property
    def release_path(self) -> str:
        if self.version != "latest":
            return f"{self._release_path}/tags"
        return self._release_path

    def download_url(self, response: dict[str, Any]) -> Optional[str]:
        pattern = re.compile(self.regex)
        for c in response["assets"]:
            url = c["browser_download_url"]
            if pattern.match(url):
                return url
        

Source: TypeAlias = Github

@dataclass
class Extractor:
    source: Source = Github()
    _content: dict[str, Any] = field(default_factory=dict)

    def download(self):
        conn = http.client.HTTPSConnection(self.source.domain)
        request_url = f"{self.source.release_path}/{self.source.version}"
        try:
            conn.request('GET', request_url, headers={"User-Agent": "curly-fries"})
            data = conn.getresponse()
            if data.status > 399:
                raise HTTPException(NOT_FOUND, request_url)
            self._content = json.loads(data.read())
        finally:
            conn.close()


    @property
    def content(self):
        return self._content

    def download_url(self):
        if not self._content:
            self.download()
        return self.source.download_url(self._content)


if __name__ == "__main__":
    args = arg_parser()
    asset = Extractor(Github(version=args.version))
    print(asset.download_url())
