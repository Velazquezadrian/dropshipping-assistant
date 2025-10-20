from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path para importar el bot
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

def home_view(request):
    """Vista principal del bot de dropshipping"""
    return HttpResponse("""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🤖 Bot Dropshipping - Panel de Control</title>
        <style>
            body {
                font-family: 'Segoe UI', Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                color: white;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                padding: 30px;
                box-shadow: 0 8px 32px rgba(31, 38, 135, 0.37);
            }
            .header {
                text-align: center;
                margin-bottom: 40px;
            }
            .header h1 {
                font-size: 3em;
                margin: 0;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .status {
                background: rgba(76, 175, 80, 0.8);
                padding: 15px;
                border-radius: 10px;
                margin: 20px 0;
                text-align: center;
                font-weight: bold;
            }
            .grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }
            .card {
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(5px);
                border-radius: 15px;
                padding: 25px;
                text-align: center;
                transition: transform 0.3s ease;
                border: 1px solid rgba(255, 255, 255, 0.2);
            }
            .card:hover {
                transform: translateY(-5px);
                background: rgba(255, 255, 255, 0.2);
            }
            .card h3 {
                margin-top: 0;
                font-size: 1.5em;
            }
            .btn {
                display: inline-block;
                padding: 12px 25px;
                background: #4CAF50;
                color: white;
                text-decoration: none;
                border-radius: 25px;
                margin: 10px 5px;
                transition: all 0.3s ease;
                font-weight: bold;
                border: 2px solid transparent;
            }
            .btn:hover {
                background: #45a049;
                transform: scale(1.05);
                border-color: white;
            }
            .btn-secondary {
                background: #2196F3;
            }
            .btn-secondary:hover {
                background: #1976D2;
            }
            .btn-execute {
                background: #FF9800;
                font-size: 1.2em;
                padding: 15px 30px;
            }
            .btn-execute:hover {
                background: #F57C00;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin: 30px 0;
            }
            .feature {
                background: rgba(255, 255, 255, 0.1);
                padding: 15px;
                border-radius: 10px;
                text-align: center;
            }
            .emoji {
                font-size: 2em;
                display: block;
                margin-bottom: 10px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🤖 Bot Dropshipping</h1>
                <p>Sistema automatizado de productos para dropshipping</p>
            </div>
            
            <div class="status">
                ✅ Servidor Django activo | 🔗 Discord configurado | 🤖 Bot funcionando
            </div>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="#" onclick="ejecutarBot()" class="btn btn-execute">
                    🚀 EJECUTAR BOT AHORA
                </a>
            </div>
            
            <div class="features">
                <div class="feature">
                    <span class="emoji">📦</span>
                    <strong>Productos Realistas</strong>
                    <p>Genera productos con precios y datos reales</p>
                </div>
                <div class="feature">
                    <span class="emoji">📱</span>
                    <strong>Discord Integrado</strong>
                    <p>Envía automáticamente a Discord</p>
                </div>
                <div class="feature">
                    <span class="emoji">🎯</span>
                    <strong>Categorías Específicas</strong>
                    <p>Gaming, Audio y Accesorios</p>
                </div>
                <div class="feature">
                    <span class="emoji">📊</span>
                    <strong>Logs Completos</strong>
                    <p>Seguimiento de todas las operaciones</p>
                </div>
            </div>
            
            <div class="grid">
                <div class="card">
                    <h3>📊 Panel de Control</h3>
                    <p>Dashboard completo con estadísticas y métricas</p>
                    <a href="/dashboard/" class="btn">Ver Dashboard</a>
                    <a href="/simple/" class="btn btn-secondary">Dashboard Simple</a>
                </div>
                
                <div class="card">
                    <h3>🔍 Buscador de Productos</h3>
                    <p>Herramienta para encontrar productos específicos</p>
                    <a href="/finder/" class="btn">Product Finder</a>
                    <a href="/api/products/" class="btn btn-secondary">API Productos</a>
                </div>
                
                <div class="card">
                    <h3>📈 Analytics</h3>
                    <p>Análisis detallado de tendencias y métricas</p>
                    <a href="/analytics/" class="btn">Ver Analytics</a>
                    <a href="/api/analytics/metrics/" class="btn btn-secondary">API Métricas</a>
                </div>
                
                <div class="card">
                    <h3>🔧 Administración</h3>
                    <p>Panel de administración de Django</p>
                    <a href="/admin/" class="btn">Admin Panel</a>
                    <a href="/health/" class="btn btn-secondary">Health Check</a>
                </div>
            </div>
            
            <div style="text-align: center; margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.3);">
                <p>🏆 <strong>Proyecto completado y funcional</strong> | Solo Discord | Listo para presentar</p>
                <p>Última actualización: Octubre 2025</p>
            </div>
        </div>
        
        <script>
            function ejecutarBot() {
                if (confirm('🤖 ¿Ejecutar el bot de dropshipping?\\n\\n✨ Esto generará 6 productos realistas\\n📱 Los enviará automáticamente a Discord\\n⏱️ Proceso toma unos segundos')) {
                    
                    // Mostrar indicador de carga
                    const btn = event.target;
                    const originalText = btn.innerHTML;
                    btn.innerHTML = '⏳ Ejecutando...';
                    btn.disabled = true;
                    
                    // Hacer la petición al bot
                    fetch('https://127.0.0.1:8443/api/execute-bot/', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                    })
                    .then(response => response.json())
                    .then(data => {
                        btn.innerHTML = originalText;
                        btn.disabled = false;
                        
                        if (data.status === 'success') {
                            alert(`🎉 ${data.message}\\n\\n📦 ${data.details}\\n📱 ${data.note}`);
                        } else {
                            alert(`❌ Error: ${data.message}`);
                        }
                    })
                    .catch(error => {
                        btn.innerHTML = originalText;
                        btn.disabled = false;
                        alert(`❌ Error de conexión: ${error.message}\\n\\n💡 Intenta ejecutar manualmente: py bot_dropshipping_final.py`);
                        console.error('Error:', error);
                    });
                }
            }
            
            // Efecto de partículas suave
            document.addEventListener('DOMContentLoaded', function() {
                console.log('🤖 Bot Dropshipping - Sistema cargado');
                console.log('📱 Para ejecutar el bot manualmente: py bot_dropshipping_final.py');
            });
        </script>
    </body>
    </html>
    """, content_type='text/html')

@csrf_exempt
@require_http_methods(["GET", "POST"])
def execute_bot_view(request):
    """Vista para ejecutar el bot desde la web"""
    try:
        # Importar y ejecutar el bot web simplificado
        from bot_web import BotDropshippingWeb
        
        # Crear instancia del bot
        bot = BotDropshippingWeb()
        
        # Ejecutar bot
        success, message = bot.ejecutar(cantidad_productos=6)
        
        if success:
            return JsonResponse({
                "status": "success", 
                "message": "¡Bot ejecutado exitosamente!", 
                "details": message,
                "note": "Revisa Discord para ver los productos"
            })
        else:
            return JsonResponse({
                "status": "error", 
                "message": message
            }, status=500)
            
    except ImportError as e:
        return JsonResponse({
            "status": "error", 
            "message": f"No se pudo importar el bot: {str(e)}",
            "suggestion": "Verifica que bot_web.py esté disponible"
        }, status=500)
    except Exception as e:
        return JsonResponse({
            "status": "error", 
            "message": f"Error ejecutando bot: {str(e)}"
        }, status=500)