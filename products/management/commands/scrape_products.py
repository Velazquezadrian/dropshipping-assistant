"""
Comando para ejecutar el scraper de productos
"""

import logging
from django.core.management.base import BaseCommand
from django.utils import timezone
from products.models import Product
from products.services.scraper import scrape_all_platforms

logger = logging.getLogger('products')


class Command(BaseCommand):
    help = 'Ejecuta el scraper para obtener productos de todas las plataformas'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--platform',
            type=str,
            help='Plataforma específica a scrapear (mock, aliexpress, etc.)',
            default=None
        )
        parser.add_argument(
            '--count',
            type=int,
            help='Número de productos a scrapear por plataforma',
            default=5
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Ejecutar en modo de prueba sin guardar en la base de datos',
        )
    
    def handle(self, *args, **options):
        platform = options['platform']
        count = options['count']
        dry_run = options['dry_run']
        
        self.stdout.write(
            self.style.SUCCESS(f'Iniciando scraping...')
        )
        
        try:
            if platform:
                # Scrapear plataforma específica
                from products.services.scraper import ScraperFactory
                scraper = ScraperFactory.get_scraper(platform)
                products = scraper.scrape_products(count=count)
                self.stdout.write(f'Scrapeados {len(products)} productos de {platform}')
            else:
                # Scrapear todas las plataformas
                products = scrape_all_platforms(count_per_platform=count)
                self.stdout.write(f'Scrapeados {len(products)} productos totales')
            
            if dry_run:
                self.stdout.write(
                    self.style.WARNING('Modo dry-run: No se guardaron productos en la base de datos')
                )
                for product in products[:3]:  # Mostrar solo los primeros 3
                    self.stdout.write(f"  - {product['title']} - ${product['price']}")
                return
            
            # Guardar productos en la base de datos
            from products.services.product_manager import bulk_import_products
            
            stats = bulk_import_products(products)
            new_products = stats['created']
            existing_products = stats['existing']
            errors = stats['errors']
            
            # Resumen
            self.stdout.write(
                self.style.SUCCESS(
                    f'Scraping completado: {new_products} productos nuevos, '
                    f'{existing_products} productos existentes'
                )
            )
            
            # Estadísticas generales
            total_products = Product.objects.count()
            recent_products = Product.objects.filter(
                created_at__gte=timezone.now() - timezone.timedelta(hours=24)
            ).count()
            
            self.stdout.write(f'Total de productos en la base de datos: {total_products}')
            self.stdout.write(f'Productos agregados en las últimas 24 horas: {recent_products}')
            
        except Exception as e:
            logger.error(f"Error en el scraping: {e}")
            self.stdout.write(
                self.style.ERROR(f'Error ejecutando scraper: {e}')
            )