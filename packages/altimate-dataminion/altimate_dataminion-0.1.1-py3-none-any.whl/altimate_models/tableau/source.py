import logging
from typing import Dict, Optional, Text

import tableauserverclient as TSC

from altimate_models.base.source import DataSource
from altimate_profiler.utils import sha256_encoding

logger = logging.getLogger(__name__)


class TableauSource(DataSource):
    """
    TableauSource represents a connection to a Tableau server.
    """

    host: Optional[str] = None
    site_name: Optional[str] = None
    pat_name: Optional[str] = None
    pat_secret: Optional[str] = None
    user: Optional[str] = None
    password: Optional[str] = None
    account: Optional[str] = None
    role: Optional[str] = None
    warehouse: Optional[str] = None
    worksheet_location:  Optional[str] = None

    @classmethod
    def prompt(cls, data_store_config: Dict):
        """Prompt for any additional configuration needed."""
        return data_store_config

    def cred_prompt(self):
        """Prompt for credentials if needed."""
        return None

    @classmethod
    def get_connection_information(cls, data_store_config: Dict):
        """Get connection information from the config."""
        data_store_config[
            "connection_info"
        ] = f"{data_store_config['host']}/{data_store_config['site_name']}"
        data_store_config["connection_hash"] = sha256_encoding(
            data_store_config["connection_info"]
        )
        return data_store_config

    def get_databases(self):
        """Get list of available databases (sites in Tableau context)."""
        if not (self.pat_name and self.pat_secret and self.host):
            return []

        try:
            # Authenticate with Tableau Server using PAT
            tableau_auth = TSC.PersonalAccessTokenAuth(
                token_name=self.pat_name,
                personal_access_token=self.pat_secret,
                site_id="",  # Empty string to list all sites
            )
            url = f"https://{self.host}"
            server = TSC.Server(url, use_server_version=True)

            with server.auth.sign_in(tableau_auth):
                # Get all available sites
                sites, _ = server.sites.get()
                # Return site content_urls as dictionaries with database_name key
                return [
                    {"database_name": site.content_url or "default"} for site in sites
                ]

        except Exception as e:
            # Log error and return empty list if connection fails
            logger.error(f"Error getting Tableau sites: {e}")
            return []

    @staticmethod
    def get_required_workbooks_and_sheets():
        """
        Get the required workbooks and their sheets for Tableau server validation.
        
        Returns:
            dict: Dictionary mapping workbook names to lists of required sheet names
        """
        return {
            'altimate_ts_events': ['access_events'],
            'altimate_ts_background_tasks': ['refresh_events'],
            'altimate_ts_users': ['user_data'],
        }

    def test_connection(self):
        """Test the connection and verify PAT has proper permissions."""
        if self.pat_name and self.pat_secret:
            tableau_auth = TSC.PersonalAccessTokenAuth(
                token_name=self.pat_name,
                personal_access_token=self.pat_secret,
                site_id=self.site_name if self.site_name != "default" else "",
            )
            url = f"https://{self.host}"
            server = TSC.Server(url, use_server_version=True)
            
            try:
                with server.auth.sign_in(tableau_auth):
                    # Get current user to check their site role
                    current_user = server.users.get_by_id(server.user_id)
                    
                    # Check if user has Site Administrator Creator or Site Administrator role
                    site_role = current_user.site_role
                    
                    # Valid roles: SiteAdministratorCreator, SiteAdministrator
                    valid_roles = ['SiteAdministratorCreator', 'SiteAdministrator']
                    
                    if site_role not in valid_roles:
                        raise Exception(
                            f"User has insufficient privileges. "
                            f"Current role: {site_role}. Required: Site Administrator Creator or Creator role."
                        )
                    
                    logger.info(f"Connection successful. User has {site_role} privileges.")
                    return True
                    
            except Exception as e:
                logger.error(f"Connection test failed: {e}")
                raise Exception(f"Failed to connect to Tableau server: {str(e)}")
        else:
            raise Exception("Missing PAT credentials")

    def get_connection_string(self, *args, **kwargs) -> Text:
        """Get connection string for Tableau."""
        return f"tableau://{self.host}/{self.site_name}"

    def drop_credentials(self):
        """Clear sensitive credentials."""
        config_dict = self.dict()
        config_dict.pop("password")
        config_dict.pop("user")
        return config_dict

    def get_resource(self):
        """Get resource information."""
        return {"url": self.host, "site": self.site_name}

    def get_identifier_and_fqn(self):
        """Get identifier and fully qualified name."""
        return (
            f"tableau://{self.host}/{self.site_name}",
            f"{self.host}/{self.site_name}",
        )

    @classmethod
    def get_resource_config(cls, resource_config: Dict):
        """Get resource configuration."""
        return resource_config

    @classmethod
    def map_config_to_source(cls, config: Dict):
        """Map configuration to source attributes."""
        connection_info = config.get("connection_info")
        if not connection_info:
            return config
        tableau_config = cls.get_config_from_url(connection_info)
        config.update(tableau_config)
        config.pop("connection_info", None)
        return config

    @classmethod
    def get_config_from_url(cls, connection_info: str):
        parts = connection_info.split("/", 1)
        if len(parts) != 2:
            raise ValueError("Invalid Tableau connection string format")
        return {"host": parts[0], "site_name": parts[1]}

    def update_credentials(self, key: str):
        """Update credentials using the provided key."""
        if ":" in key:
            pat_name, pat_secret = key.split(":", 1)
            self.pat_name = pat_name
            self.pat_secret = pat_secret
            self.user = pat_name
            self.password = pat_secret

    def override_schema(self, schema):
        """Override schema if needed."""
        return schema

    def get_connect_args(self):
        """Get connection arguments."""
        return super().get_connect_args()
