"""
Verificaciones del sistema para el comando run
"""
import os
import socket
import time
import subprocess
from urllib.parse import urlparse

import click

from tai_keycloak import kc


def check_docker_engine() -> bool:
    """Verificar que Docker Engine esté corriendo."""
    click.echo("🔍 " + click.style("Verificando Docker Engine...", fg='yellow'))
    
    try:
        result = subprocess.run(
            ['docker', 'info'], 
            capture_output=True, 
            text=True, 
            timeout=5
        )
        if result.returncode == 0:
            click.echo("   ✅ " + click.style("Docker Engine está corriendo", fg='green'))
            click.echo()
            return True
        else:
            click.echo("   ❌ " + click.style("Docker Engine no responde", fg='red'))
            click.echo("   💡 Asegúrate de que Docker Desktop esté iniciado")
            return False
    except subprocess.TimeoutExpired:
        click.echo("   ⏱️  " + click.style("Timeout verificando Docker", fg='red'))
        return False
    except FileNotFoundError:
        click.echo("   ❌ " + click.style("Docker no está instalado", fg='red'))
        click.echo("   💡 Instala Docker desde https://docker.com")
        return False
    except Exception as e:
        click.echo(f"   ❌ " + click.style(f"Error verificando Docker: {e}", fg='red'))
        return False


def check_database_connection() -> bool:
    """
    Verificar conexión a la base de datos sin usar dependencias pesadas.
    Solo para bases de datos externas (no H2).
    """
    
    db_type = os.environ.get('KC_DB', 'h2')
    
    # Si es H2, no necesitamos verificar conexión externa
    if db_type.lower() == 'h2':
        click.echo("   ℹ️  " + click.style("Usando base de datos H2 embebida", fg='cyan'))
        return True
    
    click.echo("🔍 " + click.style("Verificando conexión a base de datos...", fg='yellow'))
    
    db_url = os.environ.get('KC_DB_URL')
    if not db_url:
        click.echo("   ⚠️  " + click.style("KC_DB_URL no definida para base de datos externa", fg='yellow'))
        click.echo("   💡 Asegúrate de configurar la URL de conexión")
        return True  # No bloquear, pero avisar
    
    try:
        # Parsear URL de base de datos
        if db_url.startswith('jdbc:'):
            # Remover prefijo jdbc: para parsear
            clean_url = db_url.replace('jdbc:', '')
            if clean_url.startswith('postgresql:'):
                clean_url = clean_url.replace('postgresql:', 'postgres:')
            elif clean_url.startswith('mysql:'):
                clean_url = clean_url.replace('mysql:', 'mysql+pymysql:')
        else:
            clean_url = db_url
        
        parsed = urlparse(clean_url)
        
        if not parsed.hostname or not parsed.port:
            click.echo("   ⚠️  " + click.style("URL de base de datos mal formada", fg='yellow'))
            return True  # No bloquear
        
        # Intentar conexión TCP básica
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex((parsed.hostname, parsed.port))
        sock.close()
        
        if result == 0:
            click.echo(f"   ✅ " + click.style(f"Base de datos {db_type} accesible en {parsed.hostname}:{parsed.port}", fg='green'))
            return True
        else:
            click.echo(f"   ⚠️  " + click.style(f"No se puede conectar a {parsed.hostname}:{parsed.port}", fg='yellow'))
            click.echo("   💡 Verifica que la base de datos esté corriendo y accesible")
            click.echo("   💡 Keycloak intentará conectar al iniciar")
            return True  # No bloquear, solo avisar
            
    except Exception as e:
        click.echo(f"   ⚠️  " + click.style(f"Error verificando base de datos: {e}", fg='yellow'))
        click.echo("   💡 Keycloak intentará conectar al iniciar")
        return True  # No bloquear por errores de verificación


def wait_for_keycloak_ready(timeout: int = 60) -> bool:
    """Esperar a que Keycloak esté completamente listo para recibir peticiones."""
    
    click.echo("⏱️  " + click.style("Esperando a que Keycloak esté listo...", fg='yellow'))
    
    start_time = time.time()
    attempts = 0
    
    while time.time() - start_time < timeout:
        attempts += 1
        try:
            
            # Intentar conectar
            response = kc.admin.get_server_info(with_logs=False)
            if response.success:
                return True
                
        except Exception:
            # Keycloak aún no está listo, seguir intentando
            pass
        
        # Esperar antes del siguiente intento
        time.sleep(2)
    
    # Si llegamos aquí, se agotó el timeout
    click.echo(f"   ⏰ " + click.style(f"Timeout después de {timeout}s - el servidor puede que no esté listo", fg='yellow'))
    click.echo("   💡 " + click.style("Puedes verificar manualmente en el navegador", fg='cyan'))
    click.echo()
    
    # Aunque el health check falló, seguimos adelante por si es un problema con el endpoint
    return True


def monitor_containers(compose_dir):
    """Monitorear contenedores y mantener el proceso activo."""
    
    original_dir = os.getcwd()
    os.chdir(compose_dir)
    
    try:
        # Verificar que los contenedores estén ejecutándose
        while True:
            # Verificar estado de contenedores
            result = subprocess.run(['docker-compose', 'ps', '-q'], 
                                  capture_output=True, text=True)
            
            if result.returncode != 0 or not result.stdout.strip():
                click.echo("❌ " + click.style("Los contenedores se han detenido", fg='red'))
                break
            
            # Capturar logs internamente (sin mostrar)
            # Esto ayuda a mantener los logs disponibles pero no los muestra
            subprocess.run(['docker-compose', 'logs', '--tail=0'], 
                         capture_output=True, text=True)
            
            # Esperar antes de la siguiente verificación
            time.sleep(5)
            
    except KeyboardInterrupt:
        # El signal handler se encargará de la limpieza
        pass
    finally:
        os.chdir(original_dir)