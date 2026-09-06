import secrets
import string
import hashlib
import hmac
import os

from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    String,
    DateTime
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    Session
)

from ..errors.error_codes import ErrorCode
from ..errors.nova_error import NovaError


load_dotenv()


# ============================================================
# DATABASE MODEL
# ============================================================

class Base(DeclarativeBase):
    pass


class NovaKeyRecord(Base):
    __tablename__ = "nova_keys"

    key_id: Mapped[str] = mapped_column(
        String(100),
        primary_key=True
    )

    product: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    version: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    secret_hash: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )

    seal: Mapped[str] = mapped_column(
        String(64),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="ACTIVE"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False
    )


# ============================================================
# NOVA API KEY
# ============================================================

class NovaKey:

    # --------------------------------------------------------
    # Configuration
    # --------------------------------------------------------

    NOVA_SEAL_SECRET = os.getenv(
        "NOVA_SEAL_SECRET"
    )

    DATA_PATH = (
        Path(__file__).resolve().parent.parent / "data"
    )

    DATABASE_PATH = (
        DATA_PATH / "nova_keys.db"
    )

    DATABASE_URL = (
        f"sqlite:///{DATABASE_PATH}"
    )

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        self._initialize_database()

    # ========================================================
    # PUBLIC METHODS
    # ========================================================

    def generate(self) -> str:
        """
        Generate a new Nova API key.

        Returns:
            str: The generated Nova API key.
        """

        version = ".NV_1"

        header = (
            self._generate_header()
            + version
        )

        key_id = (
            self._generate_key_id()
        )

        secret = (
            self._generate_secret()
        )

        body = (
            self._generate_body(
                key_id,
                secret
            )
        )

        secret_hash = (
            self._hash_secret(
                secret
            )
        )

        seal = (
            self._generate_seal(
                key_id,
                version,
                secret
            )
        )

        self._save_metadata(
            key_id=key_id,
            product=header.split(".", 1)[0],
            version=version.lstrip("."),
            secret_hash=secret_hash,
            seal=seal.lstrip(".")
        )

        return (
            f"{header}"
            f"{body}"
            f"{seal}"
        )

    def verify(
        self,
        nova_api_key: str
    ) -> bool:
        """
        Verify a Nova API key.

        Returns:
            bool: True if the key is valid,
            otherwise False.
        """

        deconstructed_key = (
            self.deconstruct(
                nova_api_key
            )
        )

        key_data = (
            deconstructed_key[
                "deconstructored_nova_key"
            ]
        )

        product = (
            key_data["Header"]["product"]
        )

        version = (
            key_data["Header"]["version"]
        )

        key_id = (
            key_data["body"]["Key ID"]
        )

        secret = (
            key_data["body"]["Secret"]
        )

        seal = (
            key_data["Seal"]
        )

        # ----------------------------------------------------
        # Product validation
        # ----------------------------------------------------

        if product.lower() != "nova":
            return False

        # ----------------------------------------------------
        # Version validation
        # ----------------------------------------------------

        if version != "NV_1":
            return False

        # ----------------------------------------------------
        # Find key record
        # ----------------------------------------------------

        key_record = (
            self._get_key_record(
                key_id
            )
        )

        if key_record is None:
            return False

        # ----------------------------------------------------
        # Verify secret
        # ----------------------------------------------------

        incoming_secret_hash = (
            self._hash_secret(
                secret
            )
        )

        if not hmac.compare_digest(
            incoming_secret_hash,
            key_record.secret_hash
        ):
            return False

        # ----------------------------------------------------
        # Check key status
        # ----------------------------------------------------

        if key_record.status != "ACTIVE":
            return False

        # ----------------------------------------------------
        # Verify seal
        # ----------------------------------------------------

        expected_seal = (
            self._generate_seal(
                key_id,
                "." + version,
                secret
            )
        )

        if not hmac.compare_digest(
            expected_seal.lstrip("."),
            seal
        ):
            return False

        return True

    def deconstruct(
        self,
        nova_api_key: str
    ):
        """
        Deconstruct a Nova API key into its components.
        """

        # ----------------------------------------------------
        # Separate header, body and seal
        # ----------------------------------------------------

        header, body, seal = (
            nova_api_key.rsplit(
                ".",
                2
            )
        )

        # ----------------------------------------------------
        # Separate key ID and secret
        # ----------------------------------------------------

        key_id, secret = (
            body.rsplit(
                "_",
                1
            )
        )

        # The key ID contains a leading dot.
        key_id = "." + key_id

        # ----------------------------------------------------
        # Separate product and version
        # ----------------------------------------------------

        product, version = (
            header.rsplit(
                ".",
                1
            )
        )

        return {
            "deconstructored_nova_key": {

                "Header": {
                    "product": product,
                    "version": version
                },

                "body": {
                    "Key ID": key_id,
                    "Secret": secret,
                },

                "Seal": seal,
            },
        }

    # ========================================================
    # PRIVATE DATABASE METHODS
    # ========================================================

    def _initialize_database(self):
        """
        Create the Nova data directory and database
        if they do not already exist.
        """

        self.DATA_PATH.mkdir(
            parents=True,
            exist_ok=True
        )

        self.engine = create_engine(
            self.DATABASE_URL,
            echo=False,
            connect_args={
                "timeout": 10
            }
        )

        Base.metadata.create_all(
            self.engine
        )

    def delete(self, key_id: str) -> bool:
        with Session(self.engine) as session:
            key_record = session.get(
                NovaKeyRecord,
                key_id
            )

            if key_record is None:
                return False

            session.delete(key_record)
            session.commit()

            return True

    def _save_metadata(
        self,
        key_id: str,
        product: str,
        version: str,
        secret_hash: str,
        seal: str
    ):
        """
        Save Nova API key metadata to SQLite.
        """

        with Session(
            self.engine
        ) as session:

            key_record = NovaKeyRecord(
                key_id=key_id,
                product=product,
                version=version,
                secret_hash=secret_hash,
                seal=seal,
                status="ACTIVE",
                created_at=datetime.now(
                    timezone.utc
                )
            )

            session.add(
                key_record
            )

            session.commit()

    def _get_key_record(
        self,
        key_id: str
    ):
        """
        Find a Nova API key record by its Key ID.
        """

        with Session(
            self.engine
        ) as session:

            return session.get(
                NovaKeyRecord,
                key_id
            )

    # ========================================================
    # PRIVATE KEY GENERATION METHODS
    # ========================================================

    def _generate_body(
        self,
        key_id: str,
        secret: str
    ) -> str:

        return (
            f"{key_id}_{secret}"
        )

    def _generate_seal(
        self,
        key_id: str,
        version: str,
        secret: str
    ) -> str:

        if self.NOVA_SEAL_SECRET is None:

            raise NovaError(
                code=ErrorCode.MISSING_FIELD,
                message="MISSING NOVA_SEAL_SECRET",
                source="nova_api_key.py",
                status_code=404
            )

        message = (
            key_id
            + version
            + secret
        )

        return "." + hmac.new(

            self.NOVA_SEAL_SECRET.encode(
                "utf-8"
            ),

            message.encode(
                "utf-8"
            ),

            hashlib.sha256

        ).hexdigest()

    def _generate_header(self) -> str:

        characters = [
            "nova",
            "NOVA"
        ]

        return secrets.choice(
            characters
        )

    def _hash_secret(
        self,
        text: str
    ) -> str:

        hash_object = hashlib.sha256(
            text.encode(
                "utf-8"
            )
        )

        return hash_object.hexdigest()

    def _generate_secret(self) -> str:

        length = 64

        characters = (
            string.ascii_letters
            + string.digits
        )

        return "".join(
            secrets.choice(
                characters
            )
            for _ in range(length)
        )

    def _generate_key_id(self) -> str:

        digits = string.digits

        digit_count = secrets.choice(
            [1, 2, 3]
        )

        # ----------------------------------------------------
        # Generate random numeric section
        # ----------------------------------------------------

        random_number = "".join(
            secrets.choice(digits)
            for _ in range(digit_count)
        )

        # ----------------------------------------------------
        # Generate random ID section
        # ----------------------------------------------------

        characters = (
            string.ascii_letters
            + string.digits
        )

        random_id = "".join(
            secrets.choice(characters)
            for _ in range(12)
        )

        return (
            f".nki_{random_number}/"
            f"{random_id}"
        )
