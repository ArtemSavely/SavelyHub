import subprocess as sp
import io
import stat
from typing import IO
from subprocess import PIPE
from pathlib import Path
from pfluent import Runner


class GitService(object):
    def __init__(self, path: str):
        super(GitService, self).__init__()
        self.path = Path(path)

    @staticmethod
    def init(path: str) -> GitService:
        sp.run(["git", "init", "--bare", path])
        return GitService(path)

    def add_hook(self, name: str, hook: str) -> str:
        path = Path(self.path, 'hooks', name)
        path.write_text(hook)
        st = path.stat()
        path.chmod(st.st_mode | stat.S_IEXEC)
        return str(path)

    def inforefs(self, service: str) -> IO:
        process = sp.Popen(
            [service, "--stateless-rpc", "--advertise-refs", self.path],
            stdout=sp.PIPE,
            stderr=sp.PIPE,
        )
        stdout, stderr = process.communicate()
        process.wait()

        data = b'# service=' + service.encode()
        datalen = len(data) + 4
        datalen = b'%04x' % datalen
        data = datalen + data + b'0000' + stdout

        return io.BytesIO(data)

    def service(self, service: str, data: bytes) -> IO:
        proc = Runner(service)\
            .arg('--stateless-rpc')\
            .arg(self.path)\
            .popen(stdin=PIPE, stdout=PIPE)

        try:
            data, _ = proc.communicate(data)
        finally:
            proc.wait()

        return io.BytesIO(data)
