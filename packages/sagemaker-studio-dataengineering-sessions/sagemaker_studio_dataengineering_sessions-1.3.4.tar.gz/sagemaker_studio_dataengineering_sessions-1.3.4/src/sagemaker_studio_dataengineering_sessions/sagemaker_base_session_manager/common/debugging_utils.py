
from IPython.core.getipython import get_ipython
from IPython.display import DisplayObject
import json
import logging
from datetime import datetime

from .metadata_utils import retrieve_sagemaker_metadata_from_file

logger = logging.getLogger(__name__)

def get_cell_id():
    """
    Get the cell ID from IPython.
    
    Returns:
        str or None: The cell ID if available, None otherwise.
    """
    try:
        ip = get_ipython()
        if ip is not None and hasattr(ip, 'parent_header'):
            return ip.parent_header.get("metadata", {}).get("cellId")
        return None
    except Exception:
        logger.error("Cannot access cell id.")
        return None

def get_cell_content():
    """
    Get the content of the current cell from IPython.
    
    Returns:
        str: The cell content if available, empty string otherwise.
    """
    try:
        ip = get_ipython()
        if ip is not None and hasattr(ip, 'history_manager'):
            return ip.history_manager.get_tail(n=1, output=False, include_latest=True, raw=True)[0][-1]
        return ""
    except Exception:
        logger.error("Cannot access cell content.")
        return ""

def get_sessions_info_html(app_id, spark_ui_url, driver_log_url):
    table_root_style = "width: 75%; margin-top: var(--jp-content-heading-margin-top); margin-bottom:var(--jp-content-heading-margin-bottom); border: var(--jp-border-width) solid var(--jp-border-color2);"
    table_header_style = "text-align: left; border: var(--jp-border-width) solid var(--jp-border-color2);"
    table_row_style = "word-wrap: break-word; text-align: left; border: var(--jp-border-width) solid var(--jp-border-color2)"
    table = f"""
                <table class="session_info_table" style="{table_root_style}">
                    <tr>
                        <th style="{table_header_style}">Id</th>
                        <th style="{table_header_style}">Spark UI</th>
                        <th style="{table_header_style}">Driver logs</th>
                    </tr>
                    <tr>
                        <td class="application_id" style="{table_row_style}">{app_id}</td>
                        <td class="spark_ui_link" style="{table_row_style}"><a href="" target="_blank" log_location="{spark_ui_url}">link</a></td>
                        <td class="driver_log_link" style="{table_row_style}"><a href="" target="_blank" log_location="{driver_log_url}">link</a></td>
                    </tr>
                </table>
            """
    html = (
        table
    )

    return html
    


def get_sessions_info_json(app_id, connection_name, driver_logs_location, events_logs_location=None):	  
    session_data = {
        'id': app_id or "",
        'connection_name': connection_name or "",
        'driver_logs_location': driver_logs_location or "",
        'events_logs_location': events_logs_location or ""
    }
    
    return SessionInfoTableDisplay(session_data)
        


class SessionInfoTableDisplay(DisplayObject):
    
    def __init__(self, session_data):
        self.session_data = session_data
    
    def _repr_mimebundle_(self, include=None, exclude=None):
        bundle = {}
        bundle['application/vnd.smus.job-monitoring+json'] = self._generate_json()
        return bundle
    
    def _generate_json(self):
        # Get the entire resource metadata from file
        resource_metadata = retrieve_sagemaker_metadata_from_file()
        
        json_data = {
            "version": "1.0",
            "session": self.session_data,
            "resource_metadata": resource_metadata
        }
        
        return json.dumps(json_data, indent=2)
