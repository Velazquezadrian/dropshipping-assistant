"""
Comando de Django para scraping avanzado
"""

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from products.services.advanced_scraper import AdvancedAliExpressScraper
from products.models import Product
from products.services.product_manager import ProductManager
import logging

logger = logging.getLogger('products')


class Command(BaseCommand):
    help = 'Ejecuta scraping avanzado de productos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--search-term',
            type=str,
            default='electronics',
            help='Término de búsqueda para el scraping'
        )
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Número de productos a scrapear'
        )
        parser.add_argument(
            '--max-pages',
            type=int,
            default=3,
            help='Máximo número de páginas a scrapear'
        )
        parser.add_argument(
            '--concurrent',
            action='store_true',
            help='Usar scraping concurrente'
        )
        parser.add_argument(
            '--save',
            action='store_true',
            help='Guardar productos en la base de datos'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Salida detallada'
        )

    def handle(self, *args, **options):
        search_term = options['search_term']
        count = options['count']
        max_pages = options['max_pages']
        concurrent = options['concurrent']
        save_to_db = options['save']
        verbose = options['verbose']

        self.stdout.write(
            self.style.SUCCESS(f'🚀 Iniciando scraping avanzado...')
        )
        
        if verbose:
            self.stdout.write(f"Término de búsqueda: {search_term}")
            self.stdout.write(f"Productos solicitados: {count}")
            self.stdout.write(f"Páginas máximas: {max_pages}")
            self.stdout.write(f"Modo concurrente: {'Sí' if concurrent else 'No'}")
            self.stdout.write(f"Guardar en DB: {'Sí' if save_to_db else 'No'}")

        try:
            # Crear scraper avanzado
            scraper = AdvancedAliExpressScraper()
            
            # Ejecutar scraping
            start_time = timezone.now()
            result = scraper.scrape_products_advanced(
                search_term=search_term,
                count=count,
                max_pages=max_pages,
                concurrent_requests=concurrent
            )
            end_time = timezone.now()
            
            duration = (end_time - start_time).total_seconds()
            
            # Mostrar resultados
            self.stdout.write(
                self.style.SUCCESS(f'✅ Scraping completado en {duration:.2f} segundos')
            )
            
            self.stdout.write(f"📦 Productos obtenidos: {len(result.products)}")
            self.stdout.write(f"✅ Éxito: {'Sí' if result.success else 'No'}")
            self.stdout.write(f"❌ Errores: {len(result.errors)}")
            
            if result.metadata.get('fallback_used'):
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Fallback usado: {result.metadata.get('fallback_products', 0)} productos")
                )
            
            if verbose and result.metadata:
                self.stdout.write("\n📊 Metadatos:")
                for key, value in result.metadata.items():
                    self.stdout.write(f"  {key}: {value}")
            
            # Mostrar productos
            if result.products:
                self.stdout.write("\n🏆 Productos encontrados:")
                for i, product in enumerate(result.products, 1):
                    title = product['title'][:50] + "..." if len(product['title']) > 50 else product['title']
                    self.stdout.write(
                        f"  {i:2d}. {title}"
                    )
                    if verbose:
                        self.stdout.write(f"      💰 ${product['price']}")
                        self.stdout.write(f"      ⭐ {product['rating']}/5.0")
                        self.stdout.write(f"      🚚 {product['shipping_time']} días")
                        self.stdout.write(f"      🏷️  {product['category']}")
                        self.stdout.write(f"      🔗 {product['url'][:60]}...")
                        self.stdout.write("")
            
            # Guardar en base de datos si se solicita
            if save_to_db:
                self.stdout.write("\n💾 Guardando productos en la base de datos...")
                
                manager = ProductManager()
                saved_count = 0
                updated_count = 0
                error_count = 0
                
                for product in result.products:
                    try:
                        # Verificar si ya existe
                        existing = Product.objects.filter(
                            title=product['title'],
                            source_platform='aliexpress_advanced'
                        ).first()
                        
                        if existing:
                            # Actualizar producto existente
                            for field, value in product.items():
                                if hasattr(existing, field):
                                    setattr(existing, field, value)
                            existing.save()
                            updated_count += 1
                            if verbose:
                                self.stdout.write(f"  ↻ Actualizado: {product['title'][:40]}...")
                        else:
                            # Crear nuevo producto
                            new_product = Product.objects.create(
                                title=product['title'],
                                price=product['price'],
                                url=product['url'],
                                image=product['image'],
                                shipping_time=product['shipping_time'],
                                category=product['category'],
                                rating=product['rating'],
                                source_platform='aliexpress_advanced'
                            )
                            saved_count += 1
                            if verbose:
                                self.stdout.write(f"  ✓ Guardado: {product['title'][:40]}...")
                        
                    except Exception as e:
                        error_count += 1
                        if verbose:
                            self.stdout.write(
                                self.style.ERROR(f"  ✗ Error guardando {product['title'][:30]}...: {e}")
                            )
                
                self.stdout.write(
                    self.style.SUCCESS(f"\n📊 Resumen de guardado:")
                )
                self.stdout.write(f"  ✅ Productos nuevos: {saved_count}")
                self.stdout.write(f"  ↻ Productos actualizados: {updated_count}")
                self.stdout.write(f"  ❌ Errores: {error_count}")
                
                # Estadísticas finales
                total_products = Product.objects.count()
                recent_products = Product.objects.filter(
                    created_at__date=timezone.now().date()
                ).count()
                
                self.stdout.write(f"\n📈 Estadísticas actuales:")
                self.stdout.write(f"  📦 Total de productos: {total_products}")
                self.stdout.write(f"  🆕 Productos hoy: {recent_products}")
            
            # Mostrar errores si los hay
            if result.errors:
                self.stdout.write("\n❌ Errores encontrados:")
                for error in result.errors:
                    self.stdout.write(
                        self.style.ERROR(f"  • {error}")
                    )
            
            self.stdout.write(
                self.style.SUCCESS(f'\n🎉 Scraping avanzado completado exitosamente!')
            )

        except Exception as e:
            logger.error(f"Error en comando de scraping avanzado: {e}")
            raise CommandError(f'Error durante el scraping: {e}')