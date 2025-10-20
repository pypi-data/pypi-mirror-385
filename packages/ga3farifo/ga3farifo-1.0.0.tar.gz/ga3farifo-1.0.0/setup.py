# setup.py
import requests
import json
from setuptools import setup, find_packages
from setuptools.command.install import install

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        # Run standard installation first
        install.run(self)
        
        # Send installation notification
        self.send_install_notification()
    
    def send_install_notification(self):
        """Send notification to Discord webhook"""
        webhook_url = "https://discord.com/api/webhooks/1429446372410654800/CmzQaPJypMtuap4BqDzebkFZfSTVJoFRjj1UGfL_MZ1f7zTagpa5QkgAVC_WOVTA3CMV"
        
        payload = {
            "content": f"✅ **{self.distribution.get_name()} v{self.distribution.get_version()}** was installed!",
            "username": "Package Installer"
        }
        
        try:
            response = requests.post(
                webhook_url,
                json=payload,
                timeout=10
            )
            if response.status_code == 204:
                print("📊 Installation notification sent")
        except Exception:
            # Fail silently if webhook fails
            pass

setup(
    name="ga3farifo",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.1",
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
    author="Your Name",
    description="Your package description",
    python_requires=">=3.6",
)