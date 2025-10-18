import requests
import sys
import tqdm


class Download:
    def __init__(self, url: str, fileName: str = None, chunkSize: int = (1024 * 1024)):
        self.url = url
        self.fileName = fileName
        self.chunkSize = chunkSize

    def downloadNoBar(self):
        response = requests.get(self.url, stream=True)
        response.raise_for_status()

        if not self.fileName:
            self.fileName = self.url.split("/")[-1] or "download"

        try:
            with open(self.fileName, "wb") as file:
                for chunk in response.iter_content(chunk_size=self.chunkSize):
                    if chunk:
                        file.write(chunk)

            print(f"✔ Downloaded {self.fileName} successfully.")
        except Exception as e:
            print(f"✘ Error downloading {self.url}: {e}")

    def download(self):
        response = requests.get(self.url, stream=True)
        response.raise_for_status()
        showProgress = True

        if not self.fileName:
            self.fileName = self.url.split("/")[-1] or "download"

        totalSize = int(response.headers.get("content-length", 0))

        try:
            with open(self.fileName, "wb") as file:
                if showProgress and sys.stdout.isatty():
                    with tqdm(
                            total=totalSize if totalSize > 0 else None,
                            unit="B",
                            unit_scale=True,
                            unit_divisor=1024,
                            desc=self.fileName,
                            ascii=True,
                            ncols=80,
                            dynamic_ncols=True,
                            miniters=1,
                            file=sys.stdout
                    ) as bar:
                        for chunk in response.iter_content(chunk_size=self.chunkSize):
                            if chunk:
                                file.write(chunk)
                                bar.update(len(chunk))

                else:
                    for chunk in response.iter_content(chunk_size=self.chunkSize):
                        if chunk:
                            file.write(chunk)
            print(f"✔ Downloaded {self.fileName} successfully.")
        except Exception as e:
            print(f"✘ Error downloading {self.url}: {e}")


download = Download(url="https://www.test.com/test.txt", fileName="test.txt")
