import logging
from typing import List, Dict, Any

from celery import shared_task, states
from celery.exceptions import Ignore

from .services.scraper import ScraperFactory
from .models import Product, ScrapeJob
from django.utils import timezone
from django.conf import settings
import requests

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="products.scrape_products_async")
def scrape_products_async(self, query: str, source: str = "aliexpress_advanced", max_pages: int = 1, job_id: str | None = None) -> Dict[str, Any]:
    """
    Realiza scraping asincrónico y persiste productos nuevos.

    Args:
        query: término de búsqueda.
        source: tipo de scraper registrado en ScraperFactory.
        max_pages: páginas a intentar (el advanced scraper decide concurrente/secuencial).
    Returns:
        dict con resumen de la operación.
    """
    job = None
    if job_id:
        try:
            job = ScrapeJob.objects.get(pk=job_id)
            job.task_id = self.request.id
            job.mark_started()
        except ScrapeJob.DoesNotExist:
            job = None

    try:
        scraper = ScraperFactory.get_scraper(source)
    except ValueError as e:
        self.update_state(state=states.FAILURE, meta={"error": str(e)})
        logger.error("Scraper no encontrado: %s", e)
        if job:
            job.mark_failure(str(e))
        raise Ignore()

    try:
        if hasattr(scraper, 'scrape_products_advanced'):
            results = scraper.scrape_products_advanced(query=query, max_pages=max_pages)
            products_data: List[Dict[str, Any]] = []
            # results puede ser lista de objetos o dicts según implementación
            for r in results:
                if isinstance(r, dict):
                    products_data.append(r)
                else:
                    # fallback intentar atributos comunes
                    products_data.append(getattr(r, '__dict__', {}))
        else:
            products_data = scraper.scrape_products(query=query, max_pages=max_pages)
    except Exception as e:  # noqa
        self.update_state(state=states.FAILURE, meta={"error": str(e)})
        logger.exception("Error durante scraping async")
        if job:
            job.mark_failure(str(e))
            _notify_scrape(job, success=False)
        raise Ignore()

    total = len(products_data)
    created = 0
    for idx, pdata in enumerate(products_data, start=1):
        if not pdata:
            continue
        # Campos mínimos esperados: title, price, source
        title = pdata.get('title') or pdata.get('name')
        price = pdata.get('price') or pdata.get('price_numeric')
        if title is None or price is None:
            continue
        try:
            obj, was_created = Product.objects.get_or_create(
                title=title,
                defaults={
                    'price': price,
                    'original_price': pdata.get('original_price') or price,
                    'source': pdata.get('source', source),
                    'category': pdata.get('category') or pdata.get('category_guess') or '',
                    'url': pdata.get('url') or '',
                    'image_url': pdata.get('image_url') or '',
                    'currency': pdata.get('currency') or 'USD'
                }
            )
            if was_created:
                created += 1
        except Exception:  # noqa
            logger.debug("Producto duplicado o error al guardar", exc_info=True)
            continue

        # Actualizar progreso cada 5 ítems o al final
        if idx == total or idx % 5 == 0:
            progress = round(idx / total * 100, 2) if total else 100
            self.update_state(state=states.STARTED, meta={
                'progress': progress,
                'processed': idx,
                'created': created,
                'total': total
            })
            if job:
                job.update_progress(progress=progress, processed=idx, created=created, total=total)

    summary = {
        "query": query,
        "source": source,
        "requested_pages": max_pages,
        "returned_items": len(products_data),
        "created": created
    }
    logger.info("Scraping async completado: %s", summary)
    if job:
        job.mark_success(returned=summary['returned_items'], created=summary['created'], requested_pages=max_pages, summary=summary)
        _notify_scrape(job, success=True)
    return summary


def _notify_scrape(job: ScrapeJob, success: bool):  # pragma: no cover - side effects
    """Enviar notificación Telegram/Discord si configuración disponible."""
    try:
        text_status = '✅ FINALIZADO' if success else '❌ ERROR'
        base_msg = (
            f"{text_status} SCRAPE\n"
            f"Query: {job.query}\nSource: {job.source}\nStatus: {job.status}\n"
            f"Items devueltos: {job.returned_items} | Nuevos: {job.created_items}\n"
            f"Duración: {round(job.duration_seconds(),2)}s\n"
        )
        if job.error:
            base_msg += f"Error: {job.error[:180]}\n"

        # Telegram
        token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', '')
        if token and chat_id:
            try:
                requests.post(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    json={"chat_id": chat_id, "text": base_msg}
                )
            except Exception:
                logger.debug("Fallo enviando Telegram", exc_info=True)

        # Discord
        webhook = getattr(settings, 'DISCORD_WEBHOOK_URL', '')
        if webhook:
            try:
                requests.post(webhook, json={"content": base_msg})
            except Exception:
                logger.debug("Fallo enviando Discord", exc_info=True)
    except Exception:
        logger.debug("_notify_scrape error", exc_info=True)
