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

logger = logging.getLogger(__name__)


class CertificateManager:
    """Manage SSL/TLS certificates with automatic issuance and renewal."""

    def __init__(self, haproxy_manager=None):
        """
        Initialize certificate manager.

        Args:
            haproxy_manager: HAProxyManager instance for certificate deployment
        """
        self.haproxy_manager = haproxy_manager
        self.letsencrypt_dir = Path("/etc/letsencrypt")
        self.cert_storage_dir = Path("/var/lib/maruadmin/certificates")
        self.webroot_dir = Path("/var/www/letsencrypt")

        # Ensure directories exist
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Ensure required directories exist."""
        for directory in [self.cert_storage_dir, self.webroot_dir]:
            try:
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
                ["apt-get", "update"],
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
                ["apt-get", "install", "-y", "certbot"],
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

            # Build certbot command
            cmd = [
                "certbot", "certonly",
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
                if not wildcard:
                    logger.warning(f"DNS validation requested for non-wildcard domain: {domain}")

                # Use manual DNS or DNS plugin if available
                if dns_provider:
                    # TODO: Add DNS provider plugin support
                    # For now, use manual mode
                    cmd.extend([
                        "--manual",
                        "--preferred-challenges", "dns",
                        "-d", domain
                    ])
                else:
                    cmd.extend([
                        "--manual",
                        "--preferred-challenges", "dns",
                        "-d", domain
                    ])
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
            domain: Domain name

        Returns:
            Deployment status
        """
        try:
            if not self.haproxy_manager:
                return {
                    "status": "warning",
                    "message": "HAProxy manager not available"
                }

            cert_dir = self.letsencrypt_dir / "live" / domain
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

            cmd = ["certbot", "renew", "--non-interactive"]

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
                ["certbot", "certificates"],
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
                ["certbot", "revoke", "--cert-name", domain, "--non-interactive"],
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
                ["certbot", "delete", "--cert-name", domain, "--non-interactive"],
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
