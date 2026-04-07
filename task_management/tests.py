from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from task_management.models import Task


class CreateTaskAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('create_task')
        self.valid_payload = {
            'title': 'Write unit tests',
            'description': 'Add tests for the create_task API endpoint.',
            'completed': False,
        }
        self.invalid_payload = {
            'description': 'Missing title field',
            'completed': True,
        }

    def test_create_task_success(self):
        response = self.client.post(self.url, data=self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)

        task = Task.objects.first()
        self.assertEqual(task.title, self.valid_payload['title'])
        self.assertEqual(task.description, self.valid_payload['description'])
        self.assertEqual(task.completed, self.valid_payload['completed'])

        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['title'], task.title)

    def test_create_task_missing_title_returns_400(self):
        response = self.client.post(self.url, data=self.invalid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Task.objects.count(), 0)
        self.assertIn('title', response.data['message'])


class GetTasksAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('get_tasks')

    def test_get_tasks_when_none_exist(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 0)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Tasks retrieved successfully')

    def test_get_tasks_when_tasks_exist(self):
        # Create some tasks
        Task.objects.create(title='Task 1', description='First task', completed=False)
        Task.objects.create(title='Task 2', description='Second task', completed=True)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['data']), 2)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Tasks retrieved successfully')

        # Check ordering (by -created_at)
        self.assertEqual(response.data['data'][0]['title'], 'Task 2')  # Most recent first
        self.assertEqual(response.data['data'][1]['title'], 'Task 1')


class UpdateTaskAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('update_task')
        self.task = Task.objects.create(
            title='Original Title',
            description='Original Description',
            completed=False
        )
        self.valid_payload = {
            'task_id': self.task.id,
            'title': 'Updated Title',
            'description': 'Updated Description',
            'completed': True,
        }
        self.invalid_payload = {
            'title': 'No task_id',
            'description': 'Missing task_id field',
        }

    def test_update_task_success(self):
        response = self.client.post(self.url, data=self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, self.valid_payload['title'])
        self.assertEqual(self.task.description, self.valid_payload['description'])
        self.assertEqual(self.task.completed, self.valid_payload['completed'])

        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['data']['title'], self.task.title)

    def test_update_task_not_found(self):
        payload = self.valid_payload.copy()
        payload['task_id'] = 999  # Non-existent ID

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Task not found')

    def test_update_task_missing_task_id_returns_400(self):
        response = self.client.post(self.url, data=self.invalid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('task_id', response.data['message'])


class DeleteTaskAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('delete_task')
        self.task = Task.objects.create(
            title='Task to Delete',
            description='This will be deleted',
            completed=False
        )
        self.valid_payload = {
            'task_id': self.task.id,
        }
        self.invalid_payload = {
            'title': 'No task_id',
        }

    def test_delete_task_success(self):
        response = self.client.post(self.url, data=self.valid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Task.objects.count(), 0)
        self.assertEqual(response.data['status'], 'success')
        self.assertEqual(response.data['message'], 'Task deleted successfully')

    def test_delete_task_not_found(self):
        payload = self.valid_payload.copy()
        payload['task_id'] = 999  # Non-existent ID

        response = self.client.post(self.url, data=payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['status'], 'error')
        self.assertEqual(response.data['message'], 'Task not found')

    def test_delete_task_missing_task_id_returns_400(self):
        response = self.client.post(self.url, data=self.invalid_payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('task_id', response.data['message'])
