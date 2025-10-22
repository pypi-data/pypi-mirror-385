import typer
import subprocess
import sys
import os
import socket
from typing import List, Optional

app = typer.Typer(help="WELCOME TO VSI-CLI 1.0", no_args_is_help=True, add_completion=False)

#@app.command()
def aws(args: List[str] = typer.Argument(...)):
    """Execute AWS CLI commands"""
    cmd = ['aws'] + args
    typer.echo(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    sys.exit(result.returncode)

@app.command(help="Login to AWS SSO.")
def sso_login(profile: Optional[str] = typer.Option(None, help="AWS profile to use for SSO login.")):
    if not profile:
        config_path = os.path.expanduser('~/.aws/config')
        found_profile = None
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if line.startswith('[profile '):
                        temp_profile = line.strip()[9:-1]
                        # Check subsequent lines for sso_ until next section
                        for j in range(i + 1, len(lines)):
                            if lines[j].startswith('['):
                                break
                            if 'sso_' in lines[j]:
                                found_profile = temp_profile
                                break
                        if found_profile:
                            break
        
        if found_profile:
            #typer.echo(f"Found SSO profile: {found_profile}")
            use_profile = typer.confirm(f"Use profile [{found_profile}]?", default=True)
            if use_profile:
                profile = found_profile
            else:
                profile = typer.prompt("Enter profile name")
        else:
            typer.echo("No configured SSO profile found.")
            profile = typer.prompt("Enter profile name")
    
    cmd = ['aws', 'sso', 'login', '--profile', profile]
    #typer.echo(f"Executing: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=False)
    sys.exit(result.returncode)

@app.command(help="Configure SSO profiles.")
def configure_sso_profiles():
    typer.echo("Configuring SSO profiles...")
    cmd = ['aws', 'configure', 'sso']
    result = subprocess.run(cmd, capture_output=False)
    sys.exit(result.returncode)

@app.command(help="List configured SSO profiles.")
def list_configured_profiles():
    config_path = os.path.expanduser('~/.aws/config')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            content = f.read()
            if 'sso-session' in content:
                typer.echo("Profile/s found: " + content)
                #cmd = ['aws', 'sso', 'login']
                #subprocess.run(cmd, capture_output=False)
            else:
                typer.echo("No SSO profile configured")
    else:
        typer.echo("No AWS config found")

def find_free_port():
    """Find a free port on local machine"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]

def check_aws_cli_version():
    """Check AWS CLI version installed on machine"""
    cmd = ['aws', '--version']
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        typer.echo("AWS CLI version: " + result.stdout.strip())
    else:
        typer.echo("AWS CLI not found")

@app.command(help="Connect to bastion host via SSM with port forwarding.")
def xc_bastion(
    instance_id: Optional[str] = typer.Option(None, help="EC2 instance ID of bastion host"),
    file: Optional[str] = typer.Option(None, help="File containing list of remote_host:remote_port entries"),
    tunnels: Optional[List[str]] = typer.Option(None, help="Port forwarding: remote_host:remote_port or local_port:remote_host:remote_port")
):
    # Handle resource selection from file
    if file:
        if not os.path.exists(file):
            typer.echo(f"File not found: {file}")
            sys.exit(1)
        
        with open(file, 'r') as f:
            resources = [line.strip() for line in f if line.strip()]
        
        if not resources:
            typer.echo("No resources found in file")
            sys.exit(1)
        
        typer.echo("Available resources:")
        for i, resource in enumerate(resources, 1):
            typer.echo(f"{i}. {resource}")
        
        choices = typer.prompt("Select resource numbers (comma-separated)", type=str)
        selected_indices = [int(x.strip()) - 1 for x in choices.split(',')]
        
        if any(i < 0 or i >= len(resources) for i in selected_indices):
            typer.echo("Invalid selection")
            sys.exit(1)
        
        tunnels = [resources[i] for i in selected_indices]
        
    if not instance_id:
        instance_id = "i-08b6d2b9fa6d1fb7b"  # default
    
    if not tunnels:
        cmd = ['aws', 'ssm', 'start-session', '--target', instance_id]
    else:
        #typer.echo(f"Setting up port forwarding through bastion {instance_id}...")
        
        # Build document parameters for port forwarding
        port_params = []
        for tunnel in tunnels:
            parts = tunnel.split(':')
            
            if len(parts) == 2:
                # Auto-assign local port
                remote_host, remote_port = parts
                local_port = find_free_port()
            elif len(parts) == 3:
                # Use specified local port
                local_port, remote_host, remote_port = parts
            else:
                typer.echo(f"Invalid tunnel format: {tunnel}. Use remote_host:remote_port or local_port:remote_host:remote_port")
                sys.exit(1)
            
            port_params.append(f"{local_port}:{remote_host}:{remote_port}")
            typer.echo(f"Forwarding localhost:{local_port} --> {remote_host}:{remote_port}")
        
        cmd = [
            'aws', 'ssm', 'start-session',
            '--target', instance_id,
            '--document-name', 'AWS-StartPortForwardingSessionToRemoteHost',
            '--parameters', f'{{"host":["{port_params[0].split(":")[1]}"],"portNumber":["{port_params[0].split(":")[2]}"],"localPortNumber":["{port_params[0].split(":")[0]}"]}}',
            '--profile', 'powerUsers_SF-475550687851'
        ]
        
        # For multiple tunnels, start separate sessions
        if len(tunnels) > 1:
            typer.echo("Starting multiple tunnel sessions...")
            processes = []
            for tunnel in port_params:
                local_port, remote_host, remote_port = tunnel.split(':')
                parameters = f'{{"host":["{remote_host}"], "portNumber":["{remote_port}"], "localPortNumber":["{local_port}"]}}'
                tunnel_cmd = [
                    'aws', 'ssm', 'start-session',
                    '--target', f"{instance_id}",
                    '--document-name', 'AWS-StartPortForwardingSessionToRemoteHost',
                    '--parameters', f"{parameters}",
                    '--profile', 'powerUsers_SF-475550687851'
                ]
                #typer.echo(f"Executing: {' '.join(tunnel_cmd)}")
                proc = subprocess.Popen(tunnel_cmd)
                processes.append(proc)
            
            try:
                for proc in processes:
                    proc.wait()
            except KeyboardInterrupt:
                for proc in processes:
                    proc.terminate()
            return
    
    result = subprocess.run(cmd, capture_output=False)
    sys.exit(result.returncode)

@app.command(help="Install latest AWS CLI.")
def install_aws_cli():
    import platform
    system = platform.system().lower()
    
    if system == 'darwin':  # macOS
        typer.echo("Installing AWS CLI v2 for macOS...")
        subprocess.run(['curl', 'https://awscli.amazonaws.com/AWSCLIV2.pkg', '-o', '/tmp/AWSCLIV2.pkg'])
        subprocess.run(['sudo', 'installer', '-pkg', '/tmp/AWSCLIV2.pkg', '-target', '/'])
    elif system == 'linux':
        typer.echo("Installing AWS CLI v2 for Linux...")
        subprocess.run(['curl', 'https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip', '-o', '/tmp/awscliv2.zip'])
        subprocess.run(['unzip', '/tmp/awscliv2.zip', '-d', '/tmp/'])
        subprocess.run(['sudo', '/tmp/aws/install'])
    else:
        typer.echo(f"Unsupported platform: {system}")
        typer.echo("Please install AWS CLI v2 manually from https://aws.amazon.com/cli/")

def install_completion():
    """Install shell auto-completion"""
    shell = os.environ.get('SHELL', '').split('/')[-1]
    if shell == 'bash':
        completion_script = '_VSI_COMPLETE=bash_source vsi'
        rc_file = os.path.expanduser('~/.bashrc')
    elif shell == 'zsh':
        completion_script = '_VSI_COMPLETE=zsh_source vsi'
        rc_file = os.path.expanduser('~/.zshrc')
    else:
        return
    
    if os.path.exists(rc_file):
        with open(rc_file, 'r') as f:
            if completion_script not in f.read():
                with open(rc_file, 'a') as f:
                    f.write(f'\n# VSI CLI completion\neval "$({completion_script})"\n')
                typer.echo(f"Completion installed for {shell}")
        
if __name__ == '__main__':
    install_completion()
    app()