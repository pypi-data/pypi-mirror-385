from pathlib import Path

from gql import gql

from primitive.utils.actions import BaseAction

from ..utils.auth import guard
from .graphql.queries import authorized_keys_query

HOME_DIRECTORY = Path.home()
SSH_DIR = Path(HOME_DIRECTORY / ".ssh")
AUTHORIZED_KEYS_FILEPATH = SSH_DIR.joinpath("authorized_keys")


class Provisioning(BaseAction):
    @guard
    def get_authorized_keys(self, reservation_id: str) -> str:
        variables = {
            "reservationId": reservation_id,
        }
        query = gql(authorized_keys_query)
        result = self.primitive.session.execute(
            query, variable_values=variables, get_execution_result=True
        )
        return result.data["authorizedKeys"]

    def add_reservation_authorized_keys(self, reservation_id: str) -> None:
        if SSH_DIR.exists() is False:
            SSH_DIR.mkdir(parents=True, exist_ok=True)
            SSH_DIR.chmod(0o700)

        if AUTHORIZED_KEYS_FILEPATH.exists() is False:
            AUTHORIZED_KEYS_FILEPATH.touch()
            AUTHORIZED_KEYS_FILEPATH.chmod(0o600)

        AUTHORIZED_KEYS_BACKUP_FILEPATH = SSH_DIR.joinpath(
            f"authorized_keys.bak-{reservation_id}"
        )

        if AUTHORIZED_KEYS_FILEPATH.exists():
            AUTHORIZED_KEYS_BACKUP_FILEPATH.write_text(
                AUTHORIZED_KEYS_FILEPATH.read_text()
            )
        else:
            AUTHORIZED_KEYS_FILEPATH.touch()

        authorized_keys = self.get_authorized_keys(reservation_id=reservation_id)

        AUTHORIZED_KEYS_FILEPATH.write_text(
            AUTHORIZED_KEYS_FILEPATH.read_text()
            + f"\n## START PRIMITIVE SSH PUBLIC KEYS FOR RESERVATION ID {reservation_id}\n"
            + authorized_keys
            + f"\n## END PRIMITIVE SSH PUBLIC KEYS FOR RESERVATION ID {reservation_id}\n"
        )

        # self.primitive.sshd.reload()

    def remove_reservation_authorized_keys(self, reservation_id: str) -> None:
        AUTHORIZED_KEYS_BACKUP_FILEPATH = SSH_DIR.joinpath(
            f"authorized_keys.bak-{reservation_id}"
        )

        if AUTHORIZED_KEYS_BACKUP_FILEPATH.exists():
            AUTHORIZED_KEYS_FILEPATH.write_text(
                AUTHORIZED_KEYS_BACKUP_FILEPATH.read_text()
            )
            AUTHORIZED_KEYS_BACKUP_FILEPATH.unlink()
        else:
            AUTHORIZED_KEYS_FILEPATH.unlink()

        # self.primitive.sshd.reload()
