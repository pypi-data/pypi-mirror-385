"""
Certificate management module for automatic SSL/TLS certificate issuance and renewal.
Supports Let's Encrypt via certbot for automated certificate management.
"""

import os
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import tempfile

logger = logging.getLogger(__name__)


class CertificateManager:
    """Manage SSL/TLS certificates with automatic issuance and renewal."""

    def __init__(self, haproxy_manager=None, dns_provider_config: Optional[Dict[str, Any]] = None):
        """
        Initialize certificate manager.

        Args:
            haproxy_manager: HAProxyManager instance for certificate deployment
            dns_provider_config: DNS provider configuration for DNS-01 validation
                Example: {
                    "provider": "powerdns",
                    "api_url": "http://pdns:8081",
                    "api_key": "secret",
                    "zone": "highmaru.com"
                }
        """
        self.haproxy_manager = haproxy_manager
        self.dns_provider_config = dns_provider_config
        self.letsencrypt_dir = Path("/etc/letsencrypt")
        self.cert_storage_dir = Path("/var/lib/maruadmin/certificates")
        self.webroot_dir = Path("/var/www/letsencrypt")
        self.hook_scripts_dir = Path("/var/lib/maruadmin/certbot-hooks")

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        for directory in [self.cert_storage_dir, self.webroot_dir, self.hook_scripts_dir]:
            try:
                # Use sudo for system directories
                if str(directory).startswith('/var/www') or str(directory).startswith('/var/lib'):
                    subprocess.run(
                        ["sudo", "mkdir", "-p", str(directory)],
                        check=False,
                        capture_output=True
                    )
                    subprocess.run(
                        ["sudo", "chmod", "755", str(directory)],
                        check=False,
                        capture_output=True
                    )
                else:
                    directory.mkdir(parents=True, exist_ok=True)
                    os.chmod(directory, 0o755)
                logger.info(f"Ensured directory exists: {directory}")
            except Exception as e:
                logger.error(f"Failed to create directory {directory}: {e}")

    def check_certbot_installed(self) -> bool:
        """
        Check if certbot is installed.

        Returns:
            True if certbot is installed, False otherwise
        """
        try:
            result = subprocess.run(
                ["which", "certbot"],
                capture_output=True,
                text=True,
                check=False
            )
            return result.returncode == 0
        except Exception as e:
            logger.error(f"Error checking certbot installation: {e}")
            return False

    def install_certbot(self) -> Dict[str, Any]:
        """
        Install certbot if not already installed.

        Returns:
            Installation status
        """
        try:
            if self.check_certbot_installed():
                return {
                    "status": "success",
                    "message": "Certbot is already installed"
                }

            # Install certbot
            logger.info("Installing certbot...")
            result = subprocess.run(
                ["sudo", "apt-get", "update"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode != 0:
                return {
                    "status": "error",
                    "message": f"Failed to update package list: {result.stderr}"
                }

            result = subprocess.run(
                ["sudo", "apt-get", "install", "-y", "certbot"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                logger.info("Certbot installed successfully")
                return {
                    "status": "success",
                    "message": "Certbot installed successfully"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to install certbot: {result.stderr}"
                }

        except Exception as e:
            logger.error(f"Failed to install certbot: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def issue_certificate(
        self,
        domain: str,
        email: str,
        validation_method: str = "http",
        wildcard: bool = False,
        dns_provider: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Issue a new Let's Encrypt certificate.

        Args:
            domain: Domain name (e.g., "example.com" or "*.example.com")
            email: Contact email for Let's Encrypt
            validation_method: "http" or "dns"
            wildcard: Whether this is a wildcard certificate
            dns_provider: DNS provider name for DNS-01 validation

        Returns:
            Certificate issuance status
        """
        try:
            if not self.check_certbot_installed():
                install_result = self.install_certbot()
                if install_result["status"] != "success":
                    return install_result

            # Build certbot command (with sudo for Let's Encrypt operations)
            cmd = [
                "sudo", "certbot", "certonly",
                "--non-interactive",
                "--agree-tos",
                "--email", email
            ]

            if validation_method == "http":
                # HTTP-01 challenge using webroot
                cmd.extend([
                    "--webroot",
                    "--webroot-path", str(self.webroot_dir),
                    "-d", domain
                ])
            elif validation_method == "dns":
                # DNS-01 challenge (required for wildcards)
                # Check if DNS provider is configured
                if not self.dns_provider_config:
                    return {
                        "status": "error",
                        "message": (
                            f"DNS-01 validation for {domain} requires DNS provider configuration. "
                            "Please configure PowerDNS settings in agent configuration, "
                            "or use HTTP-01 validation for non-wildcard domains."
                        ),
                        "domain": domain
                    }

                # Create hook scripts for certbot
                hook_result = self._create_dns_hook_scripts()
                if hook_result["status"] != "success":
                    return hook_result

                # Use manual mode with auth/cleanup hooks
                cmd.extend([
                    "--manual",
                    "--preferred-challenges", "dns",
                    "--manual-auth-hook", str(self.hook_scripts_dir / "auth-hook.sh"),
                    "--manual-cleanup-hook", str(self.hook_scripts_dir / "cleanup-hook.sh"),
                    "-d", domain
                ])

                logger.info(f"Using PowerDNS for DNS-01 validation of {domain}")
            else:
                return {
                    "status": "error",
                    "message": f"Unsupported validation method: {validation_method}"
                }

            logger.info(f"Issuing certificate for {domain} using {validation_method} validation")
            logger.debug(f"Command: {' '.join(cmd)}")

            # Execute certbot
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                logger.info(f"Certificate issued successfully for {domain}")

                # Deploy certificate to HAProxy if manager is available
                if self.haproxy_manager:
                    deploy_result = self._deploy_to_haproxy(domain)
                    if deploy_result["status"] != "success":
                        logger.warning(f"Failed to deploy certificate to HAProxy: {deploy_result['message']}")

                return {
                    "status": "success",
                    "message": f"Certificate issued successfully for {domain}",
                    "domain": domain,
                    "validation_method": validation_method,
                    "issued_at": datetime.now().isoformat()
                }
            else:
                error_msg = result.stderr or result.stdout
                logger.error(f"Failed to issue certificate for {domain}: {error_msg}")
                return {
                    "status": "error",
                    "message": f"Certificate issuance failed: {error_msg}",
                    "domain": domain
                }

        except Exception as e:
            logger.error(f"Exception during certificate issuance for {domain}: {e}")
            return {
                "status": "error",
                "message": str(e),
                "domain": domain
            }

    def _deploy_to_haproxy(self, domain: str) -> Dict[str, Any]:
        """
        Deploy issued certificate to HAProxy.

        Args:
            domain: Domain name (may include wildcard prefix like *.example.com)

        Returns:
            Deployment status
        """
        try:
            if not self.haproxy_manager:
                return {
                    "status": "warning",
                    "message": "HAProxy manager not available"
                }

            # Remove wildcard prefix for cert path lookup
            # Certbot stores *.example.com as example.com
            cert_name = domain.replace('*.', '') if domain.startswith('*.') else domain

            cert_dir = self.letsencrypt_dir / "live" / cert_name
            cert_file = cert_dir / "fullchain.pem"
            key_file = cert_dir / "privkey.pem"

            if not cert_file.exists() or not key_file.exists():
                return {
                    "status": "error",
                    "message": f"Certificate files not found for {domain}"
                }

            # Read certificate and key
            with open(cert_file, 'r') as f:
                cert_content = f.read()
            with open(key_file, 'r') as f:
                key_content = f.read()

            # Add to HAProxy
            result = self.haproxy_manager.add_certificate(domain, cert_content, key_content)

            if result["status"] == "success":
                # Reload HAProxy to apply new certificate
                reload_result = self.haproxy_manager.reload_service()
                if reload_result["status"] == "success":
                    logger.info(f"Certificate deployed and HAProxy reloaded for {domain}")
                    return {
                        "status": "success",
                        "message": f"Certificate deployed successfully for {domain}"
                    }
                else:
                    return {
                        "status": "warning",
                        "message": f"Certificate deployed but HAProxy reload failed: {reload_result['message']}"
                    }
            else:
                return result

        except Exception as e:
            logger.error(f"Failed to deploy certificate to HAProxy for {domain}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def _create_dns_hook_scripts(self) -> Dict[str, Any]:
        """
        Create certbot hook scripts for PowerDNS DNS-01 validation.

        Returns:
            Creation status
        """
        try:
            import json as json_lib

            # Get DNS provider config
            config = self.dns_provider_config
            if not config or config.get("provider") != "powerdns":
                return {
                    "status": "error",
                    "message": "PowerDNS configuration not found"
                }

            # Create auth hook script
            auth_script = self.hook_scripts_dir / "auth-hook.sh"
            auth_script_content = f'''#!/bin/bash
# Certbot auth hook for PowerDNS
set -e

# PowerDNS API configuration
API_URL="{config['api_url']}"
API_KEY="{config['api_key']}"
ZONE="{config['zone']}"

# Certbot provides these environment variables
DOMAIN="$CERTBOT_DOMAIN"
VALIDATION="$CERTBOT_VALIDATION"

# Ensure zone ends with dot
if [[ ! "$ZONE" =~ \\. ]]; then
    ZONE="$ZONE."
fi

# Create ACME challenge record name
RECORD_NAME="_acme-challenge.$DOMAIN."

echo "Creating TXT record: $RECORD_NAME = $VALIDATION"

# Create TXT record via PowerDNS API
curl -X PATCH \\
    -H "X-API-Key: $API_KEY" \\
    -H "Content-Type: application/json" \\
    "$API_URL/api/v1/servers/localhost/zones/$ZONE" \\
    -d "{{\\\"rrsets\\\":[{{\\\"name\\\":\\\"$RECORD_NAME\\\",\\\"type\\\":\\\"TXT\\\",\\\"ttl\\\":120,\\\"changetype\\\":\\\"REPLACE\\\",\\\"records\\\":[{{\\\"content\\\":\\\"\\\\\\\"$VALIDATION\\\\\\\"\\\",\\\"disabled\\\":false}}]}}]}}"

# Wait for DNS propagation
echo "Waiting 30 seconds for DNS propagation..."
sleep 30

echo "Auth hook completed successfully"
'''

            # Create cleanup hook script
            cleanup_script = self.hook_scripts_dir / "cleanup-hook.sh"
            cleanup_script_content = f'''#!/bin/bash
# Certbot cleanup hook for PowerDNS
set -e

# PowerDNS API configuration
API_URL="{config['api_url']}"
API_KEY="{config['api_key']}"
ZONE="{config['zone']}"

# Certbot provides these environment variables
DOMAIN="$CERTBOT_DOMAIN"

# Ensure zone ends with dot
if [[ ! "$ZONE" =~ \\. ]]; then
    ZONE="$ZONE."
fi

# Create ACME challenge record name
RECORD_NAME="_acme-challenge.$DOMAIN."

echo "Deleting TXT record: $RECORD_NAME"

# Delete TXT record via PowerDNS API
curl -X PATCH \\
    -H "X-API-Key: $API_KEY" \\
    -H "Content-Type: application/json" \\
    "$API_URL/api/v1/servers/localhost/zones/$ZONE" \\
    -d "{{\\\"rrsets\\\":[{{\\\"name\\\":\\\"$RECORD_NAME\\\",\\\"type\\\":\\\"TXT\\\",\\\"changetype\\\":\\\"DELETE\\\"}}]}}"

echo "Cleanup hook completed successfully"
'''

            # Write scripts
            subprocess.run(
                ["sudo", "tee", str(auth_script)],
                input=auth_script_content.encode(),
                check=False,
                capture_output=True
            )
            subprocess.run(
                ["sudo", "chmod", "755", str(auth_script)],
                check=False,
                capture_output=True
            )

            subprocess.run(
                ["sudo", "tee", str(cleanup_script)],
                input=cleanup_script_content.encode(),
                check=False,
                capture_output=True
            )
            subprocess.run(
                ["sudo", "chmod", "755", str(cleanup_script)],
                check=False,
                capture_output=True
            )

            logger.info("Created certbot DNS hook scripts successfully")

            return {
                "status": "success",
                "message": "DNS hook scripts created"
            }

        except Exception as e:
            logger.error(f"Failed to create DNS hook scripts: {e}")
            return {
                "status": "error",
                "message": f"Failed to create DNS hook scripts: {str(e)}"
            }

    def renew_certificate(self, domain: Optional[str] = None) -> Dict[str, Any]:
        """
        Renew certificate(s).

        Args:
            domain: Specific domain to renew, or None to renew all expiring certificates

        Returns:
            Renewal status
        """
        try:
            if not self.check_certbot_installed():
                return {
                    "status": "error",
                    "message": "Certbot is not installed"
                }

            cmd = ["sudo", "certbot", "renew", "--non-interactive"]

            if domain:
                cmd.extend(["--cert-name", domain])
                logger.info(f"Renewing certificate for {domain}")
            else:
                logger.info("Renewing all expiring certificates")

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                # Sync renewed certificates to HAProxy
                if self.haproxy_manager:
                    sync_result = self.haproxy_manager.sync_letsencrypt_certificates()
                    if sync_result["status"] == "success":
                        # Reload HAProxy
                        self.haproxy_manager.reload_service()

                return {
                    "status": "success",
                    "message": "Certificate renewal completed",
                    "output": result.stdout
                }
            else:
                return {
                    "status": "error",
                    "message": f"Certificate renewal failed: {result.stderr}",
                    "output": result.stdout
                }

        except Exception as e:
            logger.error(f"Failed to renew certificate(s): {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def list_certificates(self) -> Dict[str, Any]:
        """
        List all managed certificates.

        Returns:
            List of certificates with details
        """
        try:
            if not self.check_certbot_installed():
                return {
                    "status": "error",
                    "message": "Certbot is not installed",
                    "certificates": []
                }

            result = subprocess.run(
                ["sudo", "certbot", "certificates"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                return {
                    "status": "success",
                    "certificates": self._parse_certificate_list(result.stdout)
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to list certificates: {result.stderr}",
                    "certificates": []
                }

        except Exception as e:
            logger.error(f"Failed to list certificates: {e}")
            return {
                "status": "error",
                "message": str(e),
                "certificates": []
            }

    def _parse_certificate_list(self, output: str) -> List[Dict[str, Any]]:
        """
        Parse certbot certificates output.

        Args:
            output: Certbot certificates command output

        Returns:
            List of certificate information
        """
        certificates = []
        current_cert = {}

        for line in output.split('\n'):
            line = line.strip()

            if line.startswith('Certificate Name:'):
                if current_cert:
                    certificates.append(current_cert)
                current_cert = {'name': line.split(':', 1)[1].strip()}
            elif line.startswith('Domains:'):
                current_cert['domains'] = line.split(':', 1)[1].strip()
            elif line.startswith('Expiry Date:'):
                current_cert['expiry_date'] = line.split(':', 1)[1].strip()
            elif line.startswith('Certificate Path:'):
                current_cert['cert_path'] = line.split(':', 1)[1].strip()
            elif line.startswith('Private Key Path:'):
                current_cert['key_path'] = line.split(':', 1)[1].strip()

        if current_cert:
            certificates.append(current_cert)

        return certificates

    def revoke_certificate(self, domain: str) -> Dict[str, Any]:
        """
        Revoke a certificate.

        Args:
            domain: Domain name

        Returns:
            Revocation status
        """
        try:
            if not self.check_certbot_installed():
                return {
                    "status": "error",
                    "message": "Certbot is not installed"
                }

            logger.info(f"Revoking certificate for {domain}")

            result = subprocess.run(
                ["sudo", "certbot", "revoke", "--cert-name", domain, "--non-interactive"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                # Remove from HAProxy
                if self.haproxy_manager:
                    self.haproxy_manager.remove_certificate(domain)
                    self.haproxy_manager.reload_service()

                return {
                    "status": "success",
                    "message": f"Certificate revoked for {domain}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to revoke certificate: {result.stderr}"
                }

        except Exception as e:
            logger.error(f"Failed to revoke certificate for {domain}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }

    def delete_certificate(self, domain: str) -> Dict[str, Any]:
        """
        Delete a certificate.

        Args:
            domain: Domain name

        Returns:
            Deletion status
        """
        try:
            if not self.check_certbot_installed():
                return {
                    "status": "error",
                    "message": "Certbot is not installed"
                }

            logger.info(f"Deleting certificate for {domain}")

            result = subprocess.run(
                ["sudo", "certbot", "delete", "--cert-name", domain, "--non-interactive"],
                capture_output=True,
                text=True,
                check=False
            )

            if result.returncode == 0:
                # Remove from HAProxy
                if self.haproxy_manager:
                    self.haproxy_manager.remove_certificate(domain)
                    self.haproxy_manager.reload_service()

                return {
                    "status": "success",
                    "message": f"Certificate deleted for {domain}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to delete certificate: {result.stderr}"
                }

        except Exception as e:
            logger.error(f"Failed to delete certificate for {domain}: {e}")
            return {
                "status": "error",
                "message": str(e)
            }
