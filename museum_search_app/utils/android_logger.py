"""
Android Debug Logger
Fil-baseret logging system for at diagnosticere billede download problemer på Android
"""

import os
import datetime
from pathlib import Path
from kivy.app import App


class AndroidLogger:
    """Fil-baseret logger for Android debugging"""
    
    def __init__(self):
        self.log_file = None
        self._setup_log_file()
    
    def _setup_log_file(self):
        """Opret log fil i app data directory"""
        try:
            app_instance = App.get_running_app()
            if app_instance:
                base_dir = Path(app_instance.user_data_dir)
            else:
                base_dir = Path.cwd()
                
            log_dir = base_dir / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            
            # Ny log fil hver dag
            today = datetime.date.today().strftime("%Y-%m-%d")
            self.log_file = log_dir / f"android_debug_{today}.log"
            
            # Log oprettelse
            self.log("INFO", "Android Logger initialiseret")
            
        except Exception as e:
            print(f"Kunne ikke oprette log fil: {e}")
            self.log_file = None
    
    def log(self, level: str, message: str):
        """
        Log besked til fil og konsol
        
        Args:
            level: Log level (INFO, WARNING, ERROR, DEBUG)
            message: Log besked
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_line = f"{timestamp} [{level}] {message}"
        
        # Print til konsol altid
        print(log_line)
        
        # Skriv til fil hvis muligt
        if self.log_file:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_line + '\n')
                    f.flush()
            except Exception as e:
                print(f"Log skrivning fejlede: {e}")
    
    def log_image_download_start(self, url: str):
        """Log start af billede download"""
        self.log("INFO", f"Starter billede download: {url}")
    
    def log_image_download_success(self, url: str, file_size: int, local_path: str):
        """Log succesfuld billede download"""
        self.log("INFO", f"Billede downloaded succesfuldt: {os.path.basename(local_path)} ({file_size} bytes)")
    
    def log_image_download_error(self, url: str, error: str):
        """Log billede download fejl"""
        self.log("ERROR", f"Billede download fejlede: {error}")
        self.log("DEBUG", f"URL var: {url}")
    
    def log_image_cache_hit(self, filename: str):
        """Log cache hit"""
        self.log("DEBUG", f"Bruger cached billede: {filename}")
    
    def log_ssl_context_creation(self):
        """Log SSL context oprettelse"""
        self.log("INFO", "SSL context oprettet med disabled certificate verification")
    
    def log_network_request(self, url: str, headers: dict):
        """Log network request detaljer"""
        self.log("DEBUG", f"Network request til: {url}")
        for key, value in headers.items():
            if key.lower() != 'authorization':  # Skjul auth header
                self.log("DEBUG", f"Header: {key}: {value}")
    
    def log_android_environment(self):
        """Log Android miljø information"""
        try:
            import platform
            self.log("INFO", f"Platform: {platform.system()} {platform.release()}")
            
            app_instance = App.get_running_app()
            if app_instance:
                self.log("INFO", f"App data dir: {app_instance.user_data_dir}")
            
            # Test SSL support
            import ssl
            self.log("INFO", f"SSL version: {ssl.OPENSSL_VERSION}")
            
        except Exception as e:
            self.log("WARNING", f"Kunne ikke log miljø info: {e}")
    
    def get_log_content(self) -> str:
        """Hent log indhold som string"""
        if not self.log_file or not self.log_file.exists():
            return "Ingen log fil fundet"
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Kunne ikke læse log fil: {e}"


# Global logger instance
android_logger = AndroidLogger()