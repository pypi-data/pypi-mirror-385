"""
Mostrar información del servicio iniciado
"""
import os
import click


def show_service_info():
    """Mostrar información del servicio iniciado."""
    click.echo()
    click.echo("🎉 " + click.style("¡Keycloak iniciado exitosamente!", fg='green', bold=True))
    click.echo()
    
    # Obtener puerto del entorno o usar default
    port = os.environ.get('KC_HTTP_PORT', '8090')
    if port == '80':
        port = '8090'  # Puerto mapeado en docker-compose
    
    # URLs útiles
    base_url = f"http://localhost:{port}"
    admin_url = f"{base_url}/admin"
    realms_url = f"{base_url}/realms/master"
    
    click.echo("🔗 " + click.style("URLs del servicio:", fg='cyan', bold=True))
    click.echo(f"   🏠 Página principal: {click.style(base_url, fg='blue', underline=True)}")
    click.echo(f"   👨‍💼 Consola de admin: {click.style(admin_url, fg='blue', underline=True)}")
    click.echo(f"   🔐 Realm master:     {click.style(realms_url, fg='blue', underline=True)}")
    click.echo()
    
    # Credenciales
    admin_user = os.environ.get('KEYCLOAK_ADMIN', 'admin')
    admin_password = os.environ.get('KEYCLOAK_ADMIN_PASSWORD', 'admin')
    
    click.echo("🔑 " + click.style("Credenciales de administrador:", fg='cyan', bold=True))
    click.echo(f"   👤 Usuario: {click.style(admin_user, fg='green')}")
    
    # Mostrar password solo si es la por defecto (para desarrollo)
    if admin_password == 'admin':
        click.echo(f"   🔒 Password: {click.style(admin_password, fg='green')} (por defecto)")
    else:
        click.echo(f"   🔒 Password: {click.style('***', fg='green')} (personalizada)")
    
    click.echo()
    
    # Comandos útiles
    click.echo("📋 " + click.style("Control del servidor:", fg='cyan', bold=True))
    click.echo("   ✋ Detener servidor: Presiona Ctrl+C (limpia automáticamente)")
    click.echo("   � Ver logs manualmente: docker-compose logs -f")
    click.echo()
    
    # Tips adicionales
    click.echo("💡 " + click.style("Tips:", fg='magenta', bold=True))
    click.echo("   🌐 El servidor puede tardar unos segundos en estar completamente listo")
    click.echo("   📊 Los logs se capturan internamente pero no se muestran")
    click.echo("   🔧 Este proceso mantendrá el servidor activo hasta que lo detengas")
    click.echo()