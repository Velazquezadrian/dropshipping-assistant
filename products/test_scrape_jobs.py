"""
Tests para endpoints de ScrapeJob: lanzamiento, historial y cancelación.
"""

import pytest
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from products.models import ScrapeJob


class ScrapeJobEndpointsTestCase(TestCase):
    """Pruebas para endpoints de ScrapeJob."""

    def setUp(self):
        self.client = APIClient()
        self.launch_url = '/products/api/scrape/async/'
        self.jobs_list_url = '/products/api/scrapes/jobs/'

    @patch('products.views.scrape_products_async')
    def test_launch_scrape_creates_job_and_returns_ids(self, mock_task):
        """Test que el endpoint de lanzamiento crea ScrapeJob y retorna task_id + job_id."""
        # Mock de la tarea Celery
        mock_result = MagicMock()
        mock_result.id = 'test-celery-task-123'
        mock_task.delay.return_value = mock_result

        payload = {
            'query': 'bluetooth headphones',
            'source': 'aliexpress_advanced',
            'max_pages': 2
        }
        
        response = self.client.post(self.launch_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        # Verificar respuesta
        self.assertIn('task_id', data)
        self.assertIn('job_id', data)
        self.assertEqual(data['status'], 'submitted')
        self.assertEqual(data['task_id'], 'test-celery-task-123')
        
        # Verificar que se creó el ScrapeJob
        job = ScrapeJob.objects.get(id=data['job_id'])
        self.assertEqual(job.query, 'bluetooth headphones')
        self.assertEqual(job.source, 'aliexpress_advanced')
        self.assertEqual(job.requested_pages, 2)
        self.assertEqual(job.status, ScrapeJob.Status.PENDING)
        self.assertEqual(job.task_id, 'test-celery-task-123')
        
        # Verificar que se llamó la tarea con argumentos correctos
        mock_task.delay.assert_called_once_with(
            query='bluetooth headphones',
            source='aliexpress_advanced',
            max_pages=2,
            job_id=str(job.id)
        )

    def test_launch_scrape_requires_query(self):
        """Test que el endpoint requiere el parámetro query."""
        payload = {'source': 'aliexpress_advanced'}
        
        response = self.client.post(self.launch_url, payload, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('query es requerido', data['error'])

    def test_list_scrape_jobs(self):
        """Test listado de ScrapeJobs con paginación."""
        # Crear algunos jobs de prueba
        job1 = ScrapeJob.objects.create(
            query='test query 1',
            source='aliexpress_advanced',
            status=ScrapeJob.Status.SUCCESS,
            returned_items=10,
            created_items=5
        )
        job2 = ScrapeJob.objects.create(
            query='test query 2',
            source='aliexpress_advanced',
            status=ScrapeJob.Status.PENDING
        )
        
        response = self.client.get(self.jobs_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['count'], 2)
        self.assertEqual(len(data['results']), 2)
        self.assertEqual(data['limit'], 20)
        self.assertEqual(data['offset'], 0)
        
        # Verificar orden (más reciente primero)
        self.assertEqual(data['results'][0]['id'], str(job2.id))
        self.assertEqual(data['results'][1]['id'], str(job1.id))

    def test_list_scrape_jobs_with_pagination(self):
        """Test paginación en listado de jobs."""
        # Crear varios jobs
        for i in range(5):
            ScrapeJob.objects.create(
                query=f'test query {i}',
                source='aliexpress_advanced'
            )
        
        response = self.client.get(self.jobs_list_url + '?limit=2&offset=1')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['count'], 5)
        self.assertEqual(len(data['results']), 2)
        self.assertEqual(data['limit'], 2)
        self.assertEqual(data['offset'], 1)

    def test_scrape_job_detail(self):
        """Test obtener detalle de un ScrapeJob específico."""
        job = ScrapeJob.objects.create(
            query='test detail query',
            source='aliexpress_advanced',
            status=ScrapeJob.Status.SUCCESS,
            returned_items=15,
            created_items=8,
            progress=100,
            meta={'test': 'data'}
        )
        
        detail_url = f'/products/api/scrapes/jobs/{job.id}/'
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['id'], str(job.id))
        self.assertEqual(data['query'], 'test detail query')
        self.assertEqual(data['status'], 'SUCCESS')
        self.assertEqual(data['returned_items'], 15)
        self.assertEqual(data['created_items'], 8)
        self.assertEqual(float(data['progress']), 100.0)
        self.assertEqual(data['meta'], {'test': 'data'})

    def test_scrape_job_detail_not_found(self):
        """Test detalle de job inexistente retorna 404."""
        import uuid
        fake_id = str(uuid.uuid4())
        detail_url = f'/products/api/scrapes/jobs/{fake_id}/'
        
        response = self.client.get(detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertIn('error', data)
        self.assertIn('no encontrado', data['error'])

    @patch('dropship_bot.celery.app.control.revoke')
    def test_cancel_pending_job_success(self, mock_revoke):
        """Test cancelar job en estado PENDING exitosamente."""
        job = ScrapeJob.objects.create(
            query='job to cancel',
            source='aliexpress_advanced',
            task_id='task-to-cancel-123',
            status=ScrapeJob.Status.PENDING
        )
        
        cancel_url = f'/products/api/scrapes/jobs/{job.id}/cancel/'
        response = self.client.post(cancel_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['status'], 'revoked')
        self.assertEqual(data['task_id'], 'task-to-cancel-123')
        
        # Verificar que se revocó en Celery
        mock_revoke.assert_called_once_with('task-to-cancel-123', terminate=True)
        
        # Verificar que el job se marcó como REVOKED
        job.refresh_from_db()
        self.assertEqual(job.status, ScrapeJob.Status.REVOKED)
        self.assertIsNotNone(job.finished_at)

    def test_cancel_job_without_task_id(self):
        """Test cancelar job sin task_id asociado."""
        job = ScrapeJob.objects.create(
            query='job without task',
            source='aliexpress_advanced',
            status=ScrapeJob.Status.PENDING
        )
        
        cancel_url = f'/products/api/scrapes/jobs/{job.id}/cancel/'
        response = self.client.post(cancel_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertEqual(data['status'], 'revoked')
        self.assertIn('sin task_id asociado', data['detail'])
        
        # Verificar que el job se marcó como REVOKED
        job.refresh_from_db()
        self.assertEqual(job.status, ScrapeJob.Status.REVOKED)

    def test_cancel_completed_job_fails(self):
        """Test que no se puede cancelar un job completado."""
        job = ScrapeJob.objects.create(
            query='completed job',
            source='aliexpress_advanced',
            status=ScrapeJob.Status.SUCCESS
        )
        
        cancel_url = f'/products/api/scrapes/jobs/{job.id}/cancel/'
        response = self.client.post(cancel_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        
        self.assertIn('error', data)
        self.assertIn('No se puede cancelar', data['error'])
        self.assertIn('SUCCESS', data['error'])
        
        # Verificar que el status no cambió
        job.refresh_from_db()
        self.assertEqual(job.status, ScrapeJob.Status.SUCCESS)

    def test_cancel_failed_job_fails(self):
        """Test que no se puede cancelar un job fallido."""
        job = ScrapeJob.objects.create(
            query='failed job',
            source='aliexpress_advanced',
            status=ScrapeJob.Status.FAILURE,
            error='Some error occurred'
        )
        
        cancel_url = f'/products/api/scrapes/jobs/{job.id}/cancel/'
        response = self.client.post(cancel_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        
        self.assertIn('No se puede cancelar', data['error'])
        self.assertIn('FAILURE', data['error'])

    def test_cancel_already_revoked_job_fails(self):
        """Test que no se puede cancelar un job ya revocado."""
        job = ScrapeJob.objects.create(
            query='revoked job',
            source='aliexpress_advanced',
            status=ScrapeJob.Status.REVOKED
        )
        
        cancel_url = f'/products/api/scrapes/jobs/{job.id}/cancel/'
        response = self.client.post(cancel_url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        
        self.assertIn('REVOKED', data['error'])

    def test_cancel_nonexistent_job(self):
        """Test cancelar job inexistente retorna 404."""
        import uuid
        fake_id = str(uuid.uuid4())
        cancel_url = f'/products/api/scrapes/jobs/{fake_id}/cancel/'
        
        response = self.client.post(cancel_url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertIn('no encontrado', data['error'])

    @patch('dropship_bot.celery.app.control.revoke')
    def test_cancel_with_celery_error(self, mock_revoke):
        """Test manejo de error al revocar en Celery."""
        mock_revoke.side_effect = Exception("Celery connection failed")
        
        job = ScrapeJob.objects.create(
            query='job with celery error',
            source='aliexpress_advanced',
            task_id='task-error-123',
            status=ScrapeJob.Status.STARTED
        )
        
        cancel_url = f'/products/api/scrapes/jobs/{job.id}/cancel/'
        response = self.client.post(cancel_url)
        
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        data = response.json()
        
        self.assertIn('Error al revocar', data['error'])
        self.assertIn('Celery connection failed', data['error'])