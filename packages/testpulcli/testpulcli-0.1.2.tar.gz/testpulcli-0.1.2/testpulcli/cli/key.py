"""Key management CLI commands."""

from typing import Optional

import click

from testpulcli.core.auth import AuthService
from testpulcli.core.key_manager import KeyManager
from testpulcli.core.pool_manager import PoolManager
from testpulcli.exceptions import APIError, AuthenticationError, KeyManagementError
from testpulcli.utils.console import Console


@click.group(name="key")
def key() -> None:
    """Create/list developer keys."""
    pass


@key.command()
@click.option("--wallet-name", required=True, prompt="Wallet name", help="Wallet name.")
@click.option(
    "--hotkey",
    prompt="Wallet hotkey, if not provided (default) will be used",
    default="default",
    help="Wallet hotkey to create developer key (use single hotkey for single dk.)"
)
@click.option("--backend-url", default="http://localhost:5000")
@click.option("--force", is_flag=True, help="Force re-authentication")
@click.option("--no-interactive", is_flag=True, help="Skip interactive payment monitoring")
def create(
    wallet_name: str,
    hotkey: str,
    backend_url: str,
    force: bool,
    no_interactive: bool,
) -> None:
    """Authenticate and create developer key invoice."""
    Console.header(f"🔐 Authenticating with '{wallet_name}'")
    try:
        # Authenticate
        auth_service = AuthService(backend_url)
        token, wallet = auth_service.authenticate_with_wallet(wallet_name, hotkey, force)

        if not token:
            Console.error("Authentication failed.")
            return

        Console.print_table(
            "✅ Authentication Complete",
            [
                f"{'Wallet:':<20} {wallet_name}",
                f"{'Token:':<20} {token[:20]}...{token[-10:]}",
            ],
        )

        # Create developer key
        if not no_interactive:
            key_manager = KeyManager(backend_url)
            result = key_manager.create_invoice(token)

            if not result:
                Console.error("Failed to create invoice + key.")
                return
            invoice_id = result["invoiceId"]
            amount = result["amountDue"]
            dest = result["receiverAddress"]

            if click.confirm(f"🚀 Proceed with {amount} TAO payment to get developer key?"):
                success = False
                import bittensor as bt

                with Console.payment_status(amount, dest):
                    # subtensor = bt.subtensor(network="test") # uncomment this for test
                    subtensor = bt.subtensor()
                    success = subtensor.transfer(wallet=wallet, dest=dest, amount=bt.Balance.from_tao(amount=amount))
                if success:
                    Console.print(f"[bold green] Successfully transferred {amount} TAO to {dest}")
                if click.confirm("Proceed with creating pool?"):
                    pool_manager = PoolManager(backend_url=backend_url)
                    pool_manager.start(token=token, wallet=wallet)
            else:
                Console.info(f"Invoice {invoice_id} created. ")

    except (AuthenticationError, KeyManagementError, APIError) as e:
        Console.error(str(e))
    except Exception as e:
        Console.error(f"Unexpected error: {e}")


@key.command()
@click.option("--wallet-name", required=True, prompt="Wallet name", help="Wallet name")
@click.option("--backend-url", default="http://localhost:5000")
@click.option("--page", default=1, help="Page number")
@click.option("--limit", default=15, help="Keys per page")
@click.option(
    "--status",
    type=click.Choice(["active", "expired", "unused"]),
    help="Filter by status",
)
def list(wallet_name: str, backend_url: str, page: int, limit: int, status: Optional[str]) -> None:
    """list all developer keys for a wallet."""
    Console.header(f"🔑 Fetching developer keys for '{wallet_name}'")

    try:
        # Get valid token
        auth_service = AuthService(backend_url)
        token = auth_service.get_valid_token(wallet_name)

        if not token:
            token, _ = auth_service.authenticate_with_wallet(wallet_name, "default", False)
            if not token:
                Console.error("Authentication failed.")
                return

        # Fetch keys
        key_manager = KeyManager(backend_url)
        result = key_manager.list_developer_keys(token, page, limit, status)
        key_manager.display_keys_list(result["keys"], result["pagination"], wallet_name)

    except (AuthenticationError, KeyManagementError, APIError) as e:
        Console.error(str(e))
    except Exception as e:
        Console.error(f"Unexpected error: {e}")


@key.group()
def invoice() -> None:
    """Invoice management commands."""
    pass


@invoice.command()
@click.argument("invoice_id")
@click.option("--wallet-name", required=True, prompt="Wallet name", help="Wallet name")
@click.option("--backend-url", default="http://localhost:5000")
def get(invoice_id: str, wallet_name: str, backend_url: str) -> None:
    """Get invoice status."""
    try:
        auth_service = AuthService(backend_url)
        token = auth_service.get_valid_token(wallet_name)

        if not token:
            Console.error("Authentication required. Run: testpulcli auth login")
            return

        key_manager = KeyManager(backend_url)
        is_paid, developer_key = key_manager.display_invoice_status(token, invoice_id)

        if is_paid:
            Console.success("Invoice has been paid!")
        else:
            Console.warning("Invoice is still pending payment.")

    except (AuthenticationError, KeyManagementError, APIError) as e:
        Console.error(str(e))
    except Exception as e:
        Console.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    key()
