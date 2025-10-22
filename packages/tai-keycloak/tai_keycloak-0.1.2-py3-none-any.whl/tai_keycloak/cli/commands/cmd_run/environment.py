"""
Configuración de variables de entorno para el comando run
"""
import os
import click
from tai_keycloak.utils import EnvironmentVariables


def setup_environment_variables():
    """Configurar y mostrar variables de entorno."""
    click.echo("⚙️  " + click.style("Configurando variables de entorno...", fg='yellow'))
    
    # Capturar estado antes
    env_before = dict(os.environ)
    
    # Configurar variables
    env_vars = EnvironmentVariables()
    env_vars.set()
    
    # Analizar qué cambió
    user_vars = []
    default_vars = []
    
    for var in env_vars.VARIABLES_TO_SET:
        current_value = os.environ.get(var)
        if current_value:
            was_set_before = env_before.get(var) == current_value
            if was_set_before and env_before.get(var):
                user_vars.append((var, current_value, "definida por usuario"))
            else:
                default_vars.append((var, current_value, "valor por defecto"))
    
    # Mostrar variables del usuario
    if user_vars:
        click.echo("   👤 " + click.style("Variables definidas por el usuario:", fg='blue'))
        for var, value, source in user_vars:
            # Ocultar passwords
            display_value = "***" if "PASSWORD" in var else value
            click.echo(f"      {var}={display_value}")
    
    # Mostrar variables por defecto
    if default_vars:
        click.echo("   🔧 " + click.style("Variables por defecto:", fg='cyan'))
        for var, value, source in default_vars:
            # Ocultar passwords
            display_value = "***" if "PASSWORD" in var else value
            click.echo(f"      {var}={display_value}")
    
    click.echo("   ✅ " + click.style("Variables de entorno configuradas", fg='green'))
    click.echo()