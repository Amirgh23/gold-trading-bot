"""Real-time alerts and notifications with multi-language support."""

import logging
from typing import Optional, Callable
from datetime import datetime
from enum import Enum
from trading_bot.i18n.translations import get_translator, Language

logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


class AlertManager:
    """Manages real-time alerts and notifications with bilingual support."""
    
    def __init__(self, language: Language = Language.ENGLISH):
        self.alerts = []
        self.callbacks = []
        self.sound_enabled = True
        self.desktop_notifications_enabled = True
        self.email_enabled = False
        self.email_config = {}
        self.translator = get_translator()
        self.translator.set_language(language)
    
    def register_callback(self, callback: Callable) -> None:
        """Register callback for alerts."""
        self.callbacks.append(callback)
    
    def set_language(self, language: Language) -> None:
        """Change alert language."""
        self.translator.set_language(language)
    
    def trigger_alert(
        self,
        title: str,
        message: str,
        level: AlertLevel = AlertLevel.INFO,
        sound: bool = True,
        desktop_notification: bool = True,
        email: bool = False,
    ) -> None:
        """
        Trigger an alert.
        
        Args:
            title: Alert title
            message: Alert message
            level: Alert severity level
            sound: Play sound alert
            desktop_notification: Show desktop notification
            email: Send email alert
        """
        alert = {
            'timestamp': datetime.now().isoformat(),
            'title': title,
            'message': message,
            'level': level.value,
        }
        
        self.alerts.append(alert)
        
        # Trigger callbacks
        for callback in self.callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
        
        # Sound alert
        if sound and self.sound_enabled:
            self._play_sound(level)
        
        # Desktop notification
        if desktop_notification and self.desktop_notifications_enabled:
            self._show_desktop_notification(title, message, level)
        
        # Email alert
        if email and self.email_enabled:
            self._send_email_alert(title, message, level)
        
        logger.info(f"Alert triggered: {title} - {message}")
    
    def _play_sound(self, level: AlertLevel) -> None:
        """Play sound alert based on level."""
        try:
            import winsound
            
            if level == AlertLevel.CRITICAL:
                # High frequency beep for critical
                winsound.Beep(1000, 500)
                winsound.Beep(1000, 500)
            elif level == AlertLevel.WARNING:
                # Medium frequency beep for warning
                winsound.Beep(800, 300)
            else:
                # Low frequency beep for info
                winsound.Beep(600, 200)
        except Exception as e:
            logger.debug(f"Could not play sound: {e}")
    
    def _show_desktop_notification(
        self,
        title: str,
        message: str,
        level: AlertLevel,
    ) -> None:
        """Show desktop notification."""
        try:
            # Try using plyer for cross-platform notifications
            try:
                from plyer import notification
                
                notification.notify(
                    title=title,
                    message=message,
                    timeout=10,
                )
            except ImportError:
                # Fallback to Windows notifications
                try:
                    from win10toast import ToastNotifier
                    
                    toaster = ToastNotifier()
                    toaster.show_toast(
                        title,
                        message,
                        duration=10,
                        threaded=True,
                    )
                except ImportError:
                    logger.debug("Desktop notifications not available")
        except Exception as e:
            logger.debug(f"Error showing desktop notification: {e}")
    
    def _send_email_alert(
        self,
        title: str,
        message: str,
        level: AlertLevel,
    ) -> None:
        """Send email alert."""
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            if not self.email_config.get('smtp_server'):
                logger.warning("Email configuration not set")
                return
            
            # Create email
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get('from_email')
            msg['To'] = self.email_config.get('to_email')
            msg['Subject'] = f"[{level.value}] {title}"
            
            body = f"{message}\n\nTimestamp: {datetime.now().isoformat()}"
            msg.attach(MIMEText(body, 'plain'))
            
            # Send email
            with smtplib.SMTP(
                self.email_config.get('smtp_server'),
                self.email_config.get('smtp_port', 587)
            ) as server:
                server.starttls()
                server.login(
                    self.email_config.get('username'),
                    self.email_config.get('password')
                )
                server.send_message(msg)
            
            logger.info(f"Email alert sent: {title}")
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
    
    def configure_email(
        self,
        smtp_server: str,
        smtp_port: int,
        from_email: str,
        to_email: str,
        username: str,
        password: str,
    ) -> None:
        """Configure email alerts."""
        self.email_config = {
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'from_email': from_email,
            'to_email': to_email,
            'username': username,
            'password': password,
        }
        self.email_enabled = True
        logger.info("Email alerts configured")
    
    def get_recent_alerts(self, limit: int = 50) -> list:
        """Get recent alerts."""
        return self.alerts[-limit:]
    
    def clear_alerts(self) -> None:
        """Clear all alerts."""
        self.alerts.clear()
        logger.info("Alerts cleared")
