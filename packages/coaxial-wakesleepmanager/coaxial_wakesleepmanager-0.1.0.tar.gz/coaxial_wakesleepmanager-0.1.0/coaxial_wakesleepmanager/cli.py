"""Command-line interface for WakeSleepManager."""

import os
import json
# Removed sys import as Click handles argv parsing now
import click
from rich.console import Console
from rich.table import Table

# Assuming these imports are correct relative to package root
from .device_manager import Device, DeviceManager
from .network_scanner import scan_network, get_device_name # Moved imports up

console = Console()
# Initialize device_manager here so it's available to all commands
device_manager = DeviceManager()

# --- Helper functions ---

# The _wake_device_handler is a helper called by the 'up' command function.
def _wake_device_handler(name: str = None):
    """Wake up one or more devices."""
    if name:
        try:
            # Ensure device exists before checking status or attempting wake
            device = device_manager.get_device(name)
            if device_manager.check_device_status(name):
                console.print(f"[yellow]Device '{name}' is already awake[/yellow]")
                return
            device_manager.wake_device(name)
            console.print(f"[green]Sent wake-up signal to device '{name}'[/green]")
        except KeyError:
            console.print(f"[red]Device '{name}' not found[/red]")
        except Exception as e: # Catch potential errors during wake_device
             console.print(f"[red]Error waking device '{name}': {e}[/red]")
    else:
        # Interactive mode when no name is provided (e.g., just 'wake' or 'wake up')
        devices = device_manager.list_devices()
        if not devices:
            console.print("[yellow]No devices configured. Use 'wakesleepmanager add' to add a device.[/yellow]")
            return

        table = Table(show_header=True)
        table.add_column("#")
        table.add_column("Name")
        table.add_column("Status")

        for i, device in enumerate(devices, 1):
            is_awake = device_manager.check_device_status(device.name)
            status = "[green]Awake[/green]" if is_awake else "[red]Sleeping[/red]"
            table.add_row(str(i), device.name, status)

        console.print(table)
        # click.prompt handles user input robustly
        choice = click.prompt("Enter the number of the device to wake (or 'all' for all devices)")

        if choice.lower() == 'all':
            for device in devices:
                 # Only try to wake if currently sleeping
                 if not device_manager.check_device_status(device.name):
                    try:
                        device_manager.wake_device(device.name)
                        console.print(f"[green]Sent wake-up signal to device '{device.name}'[/green]")
                    except Exception as e:
                         console.print(f"[red]Error waking device '{device.name}': {e}[/red]")
                 else:
                    console.print(f"[yellow]Device '{device.name}' is already awake, skipping[/yellow]")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(devices):
                    device = devices[idx]
                    if device_manager.check_device_status(device.name):
                        console.print(f"[yellow]Device '{device.name}' is already awake[/yellow]")
                    else:
                        try:
                            device_manager.wake_device(device.name)
                            console.print(f"[green]Sent wake-up signal to device '{device.name}'[/green]")
                        except Exception as e:
                            console.print(f"[red]Error waking device '{device.name}': {e}[/red]")
                else:
                    console.print("[red]Invalid device number[/red]")
            except ValueError:
                console.print("[red]Invalid input. Please enter a number or 'all'[/red]")

def find_ssh_keys(hostname_or_ip: str) -> list:
    """Find SSH keys that might be suitable for a host."""
    ssh_dir = os.path.expanduser("~/.ssh")
    if not os.path.exists(ssh_dir):
        return []

    # Common SSH key patterns
    key_patterns = [
        f"id_rsa_{hostname_or_ip}",
        f"id_ed25519_{hostname_or_ip}",
        f"id_ecdsa_{hostname_or_ip}",
        f"{hostname_or_ip}_rsa",
        f"{hostname_or_ip}_ed25519",
        f"{hostname_or_ip}_ecdsa",
        "id_rsa",
        "id_ed25519",
        "id_ecdsa"
    ]

    found_keys = []
    for pattern in key_patterns:
        key_path = os.path.join(ssh_dir, pattern)
        if os.path.exists(key_path):
            found_keys.append(key_path)

    return found_keys

def find_ssh_config_entry(hostname_or_ip: str) -> dict:
    """Check SSH config file for existing host configuration."""
    ssh_config_path = os.path.expanduser("~/.ssh/config")
    if not os.path.exists(ssh_config_path):
        return {}

    try:
        with open(ssh_config_path, 'r') as f:
            content = f.read()

        # Simple parsing - look for Host entries
        lines = content.split('\n')
        current_host = None
        config = {}

        for line in lines:
            line = line.strip()
            if line.startswith('Host ') and not line.startswith('#'):
                current_host = line.split()[1]
                config = {}
            elif current_host and line and not line.startswith('#'):
                if ' ' in line:
                    key, value = line.split(' ', 1)
                    config[key.lower()] = value

        # Check if this host matches our target
        if current_host and (current_host == hostname_or_ip or
                           current_host == '*' or
                           hostname_or_ip in current_host):
            return config
    except Exception:
        pass

    return {}

# Helper function for SSH config (called by add command)
# Keep this as a regular function, not a click command, as it's not meant to be called directly from CLI.
def setup_ssh_config(name: str):
    """Helper function to set up SSH configuration for a device."""
    try:
        device = device_manager.get_device(name)
        hostname_or_ip = device.hostname or device.ip_address

        # Check for existing SSH config
        ssh_config = find_ssh_config_entry(hostname_or_ip)
        if ssh_config:
            console.print(f"[yellow]Found existing SSH config for {hostname_or_ip}:[/yellow]")
            for key, value in ssh_config.items():
                console.print(f"  {key}: {value}")

            if click.confirm("Use existing SSH config?"):
                username = ssh_config.get('user', '')
                key_path = ssh_config.get('identityfile', '')
                if key_path:
                    key_path = os.path.expanduser(key_path)
                device_manager.setup_ssh_config(name, username, key_path=key_path if key_path else None)
                console.print(f"[green]SSH configuration for device '{name}' updated successfully[/green]")
                return

        # Look for SSH keys
        found_keys = find_ssh_keys(hostname_or_ip)
        if found_keys:
            console.print(f"[yellow]Found potential SSH keys for {hostname_or_ip}:[/yellow]")
            for i, key in enumerate(found_keys, 1):
                console.print(f"  {i}. {key}")

            if click.confirm("Use one of these keys?"):
                if len(found_keys) == 1:
                    selected_key = found_keys[0]
                else:
                    try:
                        choice = click.prompt("Enter key number", type=int)
                        if 1 <= choice <= len(found_keys):
                            selected_key = found_keys[choice - 1]
                        else:
                            console.print("[red]Invalid choice[/red]")
                            return
                    except ValueError:
                        console.print("[red]Invalid input[/red]")
                        return

                username = click.prompt("Enter SSH username")
                device_manager.setup_ssh_config(name, username, key_path=selected_key)
                console.print(f"[green]SSH configuration for device '{name}' updated successfully[/green]")
                return

        # Manual setup
        username = click.prompt("Enter SSH username")
        auth_type = click.prompt(
            "Choose authentication type",
            type=click.Choice(['password', 'key']),
            default='password'
        )

        if auth_type == 'password':
            password = click.prompt("Enter SSH password", hide_input=True)
            device_manager.setup_ssh_config(name, username, password=password)
        else:
            key_path = click.prompt("Enter path to SSH private key file")
            key_path = os.path.expanduser(key_path)
            if not os.path.exists(key_path):
                console.print(f"[red]SSH key file not found: {key_path}[/red]")
                return
            device_manager.setup_ssh_config(name, username, key_path=key_path)

        console.print(f"[green]SSH configuration for device '{name}' updated successfully[/green]")
    except KeyError:
        console.print(f"[red]Device '{name}' not found[/red]")
    except ValueError as e:
        console.print(f"[red]Error: {str(e)}[/red]")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred during SSH setup: {e}[/red]")


def _show_setup_menu(ctx):
    """Show the interactive setup menu for managing devices."""
    while True:
        devices = device_manager.list_devices()

        # Create main menu table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("#", style="dim", width=3)
        table.add_column("Name", min_width=15)
        table.add_column("IP Address", min_width=15)
        table.add_column("MAC Address", min_width=17)
        table.add_column("Hostname", min_width=20)
        table.add_column("SSH Config", min_width=12)
        table.add_column("Status", min_width=10)

        for i, device in enumerate(devices, 1):
            is_awake = device_manager.check_device_status(device.name)
            status = "[green]Awake[/green]" if is_awake else "[red]Sleeping[/red]"
            ssh_status = "Configured" if device.ssh_config else "Not configured"
            table.add_row(
                str(i),
                device.name,
                device.ip_address,
                device.mac_address,
                device.hostname or "N/A",
                ssh_status,
                status
            )

        console.print("\n[bold cyan]WakeSleepManager - Device Setup[/bold cyan]")
        console.print(table)

        if not devices:
            console.print("[yellow]No devices configured.[/yellow]")

        # Show menu options
        console.print("\n[bold]Options:[/bold]")
        console.print("  [green]a[/green] - Add new device")
        if devices:
            console.print("  [green]e[/green] - Edit device")
            console.print("  [green]r[/green] - Remove device")
            console.print("  [green]s[/green] - Setup SSH for device")
        console.print("  [green]q[/green] - Quit")

        choice = click.prompt("\nEnter your choice", default="q").lower()

        if choice == 'q':
            break
        elif choice == 'a':
            # Add new device - call the add command directly
            ctx.invoke(add, name=None)
        elif choice == 'e' and devices:
            # Edit device
            try:
                device_choice = click.prompt("Enter device number to edit", type=int)
                if 1 <= device_choice <= len(devices):
                    device = devices[device_choice - 1]
                    console.print(f"\n[bold]Editing device: {device.name}[/bold]")

                    # Get new values
                    new_name = click.prompt("Enter new name", default=device.name)
                    new_ip = click.prompt("Enter new IP address", default=device.ip_address)
                    new_mac = click.prompt("Enter new MAC address", default=device.mac_address)
                    new_hostname = click.prompt("Enter new hostname", default=device.hostname or "")

                    # Remove old device and add new one
                    device_manager.remove_device(device.name)
                    new_device = Device(
                        name=new_name,
                        ip_address=new_ip,
                        mac_address=new_mac,
                        hostname=new_hostname or None
                    )
                    device_manager.add_device(new_device)
                    console.print(f"[green]Device '{new_name}' updated successfully[/green]")
                else:
                    console.print("[red]Invalid device number[/red]")
            except ValueError:
                console.print("[red]Invalid input[/red]")
        elif choice == 'r' and devices:
            # Remove device
            try:
                device_choice = click.prompt("Enter device number to remove", type=int)
                if 1 <= device_choice <= len(devices):
                    device = devices[device_choice - 1]
                    if click.confirm(f"Are you sure you want to remove device '{device.name}'?"):
                        device_manager.remove_device(device.name)
                        console.print(f"[green]Device '{device.name}' removed successfully[/green]")
                else:
                    console.print("[red]Invalid device number[/red]")
            except ValueError:
                console.print("[red]Invalid input[/red]")
        elif choice == 's' and devices:
            # Setup SSH for device
            try:
                device_choice = click.prompt("Enter device number to setup SSH", type=int)
                if 1 <= device_choice <= len(devices):
                    device = devices[device_choice - 1]
                    setup_ssh_config(device.name)
                else:
                    console.print("[red]Invalid device number[/red]")
            except ValueError:
                console.print("[red]Invalid input[/red]")
        else:
            console.print("[red]Invalid choice[/red]")


# --- Click Commands ---

# Main group.
# invoke_without_command=True allows the group itself to be invoked if no subcommand is given.
# @click.pass_context is needed to use ctx.invoke to call subcommands internally.
@click.group(invoke_without_command=True)
@click.option('-s', '--setup', is_flag=True, help='Interactive setup menu for managing devices')
@click.pass_context
def cli(ctx, setup: bool):
    """WakeSleepManager - Control network devices remotely.

       Invoke with a command (list, add, check, up, sleep, remove)
       or provide a device name directly (defaults to waking up).
    """
    # If setup flag is provided, show the interactive setup menu
    if setup:
        _show_setup_menu(ctx)
        return

    # If no subcommand was explicitly invoked (e.g., called as 'wake devicename' or just 'wake')
    # Click puts the remaining arguments in ctx.args.
    # The 'up' command handles the case where 'name' is None (interactive) or provided.
    # So, if no subcommand was given, we default to invoking the 'up' command.
    # Click automatically passes arguments from ctx.args to the 'up' command.
    if ctx.invoked_subcommand is None:
        # Invoke the 'up' command using the context.
        # Click handles mapping ctx.args to wake_up's parameters.
        ctx.invoke(wake_up)


@cli.command(name="up")
@click.argument('name', required=False)
def wake_up(name: str = None):
    """Wake up one or more devices.
       Provide a device name or run interactively to choose.
       This is the default command if a device name is provided without a command.
    """
    # The core logic is in the helper function, which handles the interactive case.
    _wake_device_handler(name)

@cli.command()
@click.argument('name', required=False)
def check(name: str = None):
    """Check the status of one or more devices.
       Provide a device name or check all.
    """
    if name:
        try:
            device = device_manager.get_device(name) # Ensure device exists
            is_awake = device_manager.check_device_status(name)
            status = "[green]Awake[/green]" if is_awake else "[red]Sleeping[/red]"
            console.print(f"Device '{name}' is {status}")
        except KeyError:
            console.print(f"[red]Device '{name}' not found[/red]")
        except Exception as e:
             console.print(f"[red]Error checking status for '{name}': {e}[/red]")
    else:
        devices = device_manager.list_devices()
        if not devices:
             console.print("[yellow]No devices configured. Use 'wakesleepmanager add' to add a device.[/yellow]")
             return

        table = Table(show_header=True)
        table.add_column("Name", min_width=15)
        table.add_column("IP Address", min_width=15)
        table.add_column("MAC Address", min_width=17)
        table.add_column("Hostname", min_width=20)
        table.add_column("Status", min_width=10)

        for device in devices:
            is_awake = device_manager.check_device_status(device.name)
            status = "[green]Awake[/green]" if is_awake else "[red]Sleeping[/red]"
            table.add_row(device.name, device.ip_address, device.mac_address, device.hostname or "N/A", status)

        console.print(table)


@cli.command(name="list") # Renamed function to avoid shadowing built-in list()
def list_devices_command():
    """List all configured devices."""
    devices = device_manager.list_devices()
    if not devices:
        console.print("[yellow]No devices configured. Use 'wakesleepmanager add' to add a device.[/yellow]")
        return

    table = Table(show_header=True)
    table.add_column("Name", min_width=15)
    table.add_column("IP Address", min_width=15)
    table.add_column("MAC Address", min_width=17)
    table.add_column("Hostname", min_width=20)

    for device in devices:
        table.add_row(
            device.name,
            device.ip_address,
            device.mac_address,
            device.hostname or "N/A"
        )

    console.print(table)

@cli.command()
@click.argument('name', required=False)
def add(name: str = None):
    """Add a new device.
       Provide a device name or run interactively.
    """
    # network_scanner imports are now at the top
    if not name:
        name = click.prompt("Enter device name")

    input_method = click.prompt(
        "Choose input method",
        type=click.Choice(['scan', 'manual']),
        default='scan'
    )

    ip_address = None
    mac_address = None
    hostname = "" # Initialize hostname before potential manual input

    if input_method == 'scan':
         console.print("[yellow]Scanning network for devices...[/yellow]")
         # Pass console if scan_network needs it for output, otherwise assume it's quiet or uses its own.
         devices = scan_network()

         if devices:
             table = Table(show_header=True, header_style="bold magenta")
             table.add_column("#", style="dim")
             table.add_column("IP Address")
             table.add_column("MAC Address")
             table.add_column("Hostname")

             for i, device in enumerate(devices, 1):
                 # Ensure get_device_name doesn't crash if network fails during scan
                 hostname = get_device_name(device.get('ip_address', '')) or 'Unknown'
                 table.add_row(
                     str(i),
                     device.get('ip_address', 'N/A'),
                     device.get('mac_address', 'N/A'),
                     hostname
                 )

             console.print(table)
             choice = click.prompt("Enter the number of the device to add", type=str)

             # Validate choice and extract info
             if choice.isdigit() and 1 <= int(choice) <= len(devices):
                 selected_device = devices[int(choice) - 1]
                 ip_address = selected_device.get('ip_address')
                 mac_address = selected_device.get('mac_address')
                 hostname = get_device_name(ip_address) or '' if ip_address else '' # Get hostname for selected
             else:
                 console.print("[red]Invalid choice or cancelled. Switching to manual input.[/red]")
                 input_method = 'manual'
         else:
             console.print("[yellow]No devices found. Switching to manual input.[/yellow]")
             input_method = 'manual'

    # If scan failed or user chose manual, proceed with manual input
    if input_method == 'manual':
         ip_address = click.prompt("Enter IP address")
         mac_address = click.prompt("Enter MAC address")
         hostname = click.prompt("Enter hostname (optional)", default="")

    # Check if we got necessary info from either method
    if not name or not ip_address or not mac_address:
        # This should only happen if user somehow cancels prompts, but good check
        console.print("[red]Device information not fully provided. Aborting add.[/red]")
        return

    try:
        device = Device(
            name=name,
            ip_address=ip_address,
            mac_address=mac_address,
            hostname=hostname or None # Store empty string as None
        )
        device_manager.add_device(device)
        console.print(f"[green]Device '{name}' added successfully[/green]")

        if click.confirm("Do you want to setup SSH to be able to use the sleep command?"):
            setup_ssh_config(name)
    except ValueError as e:
        console.print(f"[red]Error adding device: {str(e)}[/red]")
    except Exception as e:
         console.print(f"[red]An unexpected error occurred during add: {e}[/red]")


@cli.command()
@click.argument('name') # Name is required for remove, Click handles this
def remove(name: str):
    """Remove a device."""
    try:
        if click.confirm(f"Are you sure you want to remove device '{name}'?"):
            device_manager.remove_device(name)
            console.print(f"[green]Device '{name}' removed successfully[/green]")
    except KeyError:
        console.print(f"[red]Device '{name}' not found[/red]")
    except Exception as e:
        console.print(f"[red]An unexpected error occurred during remove: {e}[/red]")


@cli.command()
def config():
    """Show configuration file location and status."""
    config_dir = device_manager.config_dir
    devices_file = device_manager.devices_file

    console.print(f"\n[bold cyan]WakeSleepManager Configuration[/bold cyan]")
    console.print(f"📁 Config directory: {config_dir}")
    console.print(f"📄 Devices file: {devices_file}")

    if os.path.exists(devices_file):
        try:
            with open(devices_file, 'r') as f:
                data = json.load(f)
            console.print(f"📊 Devices configured: {len(data)}")

            if data:
                table = Table(show_header=True)
                table.add_column("Name")
                table.add_column("IP Address")
                table.add_column("SSH Config")

                for name, device_data in data.items():
                    ssh_status = "Configured" if device_data.get('ssh_config') else "Not configured"
                    table.add_row(name, device_data.get('ip_address', 'N/A'), ssh_status)

                console.print(table)
        except Exception as e:
            console.print(f"[red]Error reading config: {e}[/red]")
    else:
        console.print("[yellow]No configuration file found[/yellow]")

@cli.command(name="sleep") # Command name is 'sleep'
@click.argument('name', required=False) # Argument 'name' is optional
def sleep_device_command(name: str = None): # Function name can be descriptive
    """Put one or more devices to sleep.
       Provide a device name or run interactively to choose.
    """
    if name:
        try:
            device = device_manager.get_device(name) # Ensure device exists
            if not device_manager.check_device_status(name):
                console.print(f"[yellow]Device '{name}' is already sleeping[/yellow]")
                return
            try:
                device_manager.sleep_device(name)
                console.print(f"[green]Sent sleep signal to device '{name}'[/green]")
            except (ValueError, RuntimeError) as e:
                console.print(f"[red]Error: {str(e)}[/red]")
            except Exception as e:
                console.print(f"[red]An unexpected error occurred during sleep for '{name}': {e}[/red]")
        except KeyError:
            console.print(f"[red]Device '{name}' not found[/red]")
    else:
        # Interactive mode when no name is provided (e.g., just 'sleep')
        devices = device_manager.list_devices()
        if not devices:
            console.print("[yellow]No devices configured. Use 'wakesleepmanager add' to add a device.[/yellow]")
            return

        table = Table(show_header=True)
        table.add_column("#")
        table.add_column("Name")
        table.add_column("Status")
        table.add_column("SSH Config")

        for i, device in enumerate(devices, 1):
            is_awake = device_manager.check_device_status(device.name)
            status = "[green]Awake[/green]" if is_awake else "[red]Sleeping[/red]"
            ssh_status = "Configured" if device.ssh_config else "Not configured"
            table.add_row(str(i), device.name, status, ssh_status)

        console.print(table)
        choice = click.prompt("Enter the number of the device to sleep (or 'all' for all devices)")

        if choice.lower() == 'all':
            for device in devices:
                if device_manager.check_device_status(device.name): # Only try to sleep if awake
                    try:
                        device_manager.sleep_device(device.name)
                        console.print(f"[green]Sent sleep signal to device '{device.name}'[/green]")
                    except (ValueError, RuntimeError) as e:
                        console.print(f"[red]Error with device '{device.name}': {str(e)}[/red]")
                    except Exception as e:
                         console.print(f"[red]An unexpected error occurred during sleep for '{device.name}': {e}[/red]")
                else:
                     console.print(f"[yellow]Device '{device.name}' is already sleeping, skipping[/yellow]")
        else:
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(devices):
                    device = devices[idx]
                    if not device_manager.check_device_status(device.name):
                        console.print(f"[yellow]Device '{device.name}' is already sleeping[/yellow]")
                    else:
                        try:
                            device_manager.sleep_device(device.name)
                            console.print(f"[green]Sent sleep signal to device '{device.name}'[/green]")
                        except (ValueError, RuntimeError) as e:
                            console.print(f"[red]Error: {str(e)}[/red]")
                        except Exception as e:
                            console.print(f"[red]An unexpected error occurred during sleep for '{device.name}': {e}[/red]")
                else:
                    console.print("[red]Invalid device number[/red]")
            except ValueError:
                console.print("[red]Invalid input. Please enter a number or 'all'[/red]")

# Remove wake_cli() and sleep_cli() functions

# This block is primarily for testing using `python -m wakesleepmanager.cli`
if __name__ == '__main__':
    # When run directly, Click handles parsing sys.argv and dispatching
    cli()