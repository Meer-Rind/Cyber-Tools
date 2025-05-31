from django import template

register = template.Library()

@register.filter
def get_service_name(port):
    # Common port to service mapping
    port_service_map = {
        20: 'FTP (Data)',
        21: 'FTP (Control)',
        22: 'SSH',
        23: 'Telnet',
        25: 'SMTP',
        53: 'DNS',
        80: 'HTTP',
        110: 'POP3',
        143: 'IMAP',
        443: 'HTTPS',
        3306: 'MySQL',
        3389: 'RDP',
        # Add more ports as needed
    }
    return port_service_map.get(int(port), 'Unknown')