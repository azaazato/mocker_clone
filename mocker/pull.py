import requests
import os
import json
import tarfile
from mocker import _base_dir_
import sys
print(sys.path)
from .base import BaseDockerCommand


class PullCommand(BaseDockerCommand):
    registry_base = 'https://registry-1.docker.io/v2'

    def __init__(self, *args, **kwargs):
        self.image = kwargs['<name>']
        self.library = 'library'
        self.tag = kwargs['<tag>'] if kwargs['<tag>'] is not None else 'latest'
        self.headers = None

    def auth(self, library, image):
        token_req = requests.get(
            f'https://auth.docker.io/token?service=registry.docker.io&scope=repository:{library}/{image}:pull'
        )
        return token_req.json()['token']

    def get_manifest(self):
        print(f"Fetching manifest for {self.image}:{self.tag}...")

        manifest = requests.get(f'{self.registry_base}/{self.library}/{self.image}/manifests/{self.tag}',
                                headers=self.headers)

        return manifest.json()

    def run(self, *args, **kwargs):
        self.headers = {'Authorization': f'Bearer {self.auth(self.library, self.image)}'}

        manifest = self.get_manifest()

        image_name_friendly = manifest['name'].replace('/', '_')
        with open(os.path.join(_base_dir_, image_name_friendly+'.json'), 'w') as cache:
            cache.write(json.dumps(manifest))

        dl_path = os.path.join(_base_dir_, image_name_friendly, 'layers')
        if not os.path.exists(dl_path):
            os.makedirs(dl_path)

        layer_sigs = [layer['blobSum'] for layer in manifest['fsLayers']]
        unique_layer_sigs = set(layer_sigs)

        contents_path = os.path.join(dl_path, 'contents')
        if not os.path.exists(contents_path):
            os.makedirs(contents_path)

        for sig in unique_layer_sigs:
            print(F'Fetching layer {sig}..')
            url = f'{self.registry_base}/{self.library}/{self.image}/blobs/{sig}'
            local_filename = os.path.join(dl_path, sig) + '.tar'

            r = requests.get(url, stream=True, headers=self.headers)
            with open(local_filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)

            with tarfile.open(local_filename, 'r') as tar:
                for member in tar.getmembers()[:10]:
                    print('- ' + member.name)
                print('...')

                tar.extractall(str(contents_path))


