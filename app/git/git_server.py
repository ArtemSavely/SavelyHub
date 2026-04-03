from app import Config
from pathlib import Path
import subprocess as sp


class GitServer:
    def __init__(self):
        self.repos_base = Path(Config.REPOS_BASE_DIR)
        self.repos_base.mkdir(exist_ok=True, parents=True)

    def create_bare_repo(self, owner: str, repo_name: str):
        repo_path = Path(self.repos_base, owner, f"{repo_name}.git")
        repo_path.parent.mkdir(exist_ok=True, parents=True)

        if repo_path.exists():
            raise ValueError("Репозиторий уже существует")

        sp.run(["git", "init", "--bare"])
        return repo_path

    def inforefs(self, owner: str, repo_name: str, service: str):
        repo_path = Path(self.repos_base, owner, f"{repo_name}.git")
        process = sp.Popen(
            [service, "--stateless-rpc", "--advertise-refs", repo_path],
            stdout=sp.PIPE,
            stderr=sp.PIPE,
        )
        stdout, stderr = process.communicate()
        process.wait()

        header = f"# service={service}".encode()
        datalen = len(header)
        datalen_hex = f"{datalen:04x}".encode()
        packet = datalen_hex + header + b"0000"
        return packet + stdout
