import { useState, useEffect } from 'react'
import api from '../../services/api'
import { usePermissions } from '../../hooks/usePermissions'
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'

function TaskTypeModal({ taskType, onClose }) {
  const [formData, setFormData] = useState({
    name: '',
    is_active: true,
  })
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (taskType) {
      setFormData({
        name: taskType.name || '',
        is_active: taskType.is_active ?? true,
      })
    }
  }, [taskType])

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      if (taskType) {
        await api.patch(`/tasks/types/${taskType.id}/`, formData)
      } else {
        await api.post('/tasks/types/', formData)
      }
      onClose()
    } catch (error) {
      setError(error.response?.data?.error || error.response?.data?.name?.[0] || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-1/2 lg:w-1/3 shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold">
            {taskType ? 'Edit Task Type' : 'Create Task Type'}
          </h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-800 text-sm">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Name *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_active"
              checked={formData.is_active}
              onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
              className="mr-2"
            />
            <label htmlFor="is_active" className="text-sm font-medium text-gray-700">
              Active
            </label>
          </div>

          <div className="flex justify-end space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Saving...' : taskType ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

function TaskTypes() {
  const { hasPermission } = usePermissions()
  const [taskTypes, setTaskTypes] = useState([])
  const [loading, setLoading] = useState(true)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedTaskType, setSelectedTaskType] = useState(null)

  // Check read permission
  if (!hasPermission('tasks', 'read')) {
    return (
      <div className="text-center py-12 text-gray-500">
        You do not have permission to access this page.
      </div>
    )
  }

  useEffect(() => {
    fetchTaskTypes()
  }, [])

  const fetchTaskTypes = async () => {
    try {
      setLoading(true)
      const response = await api.get('/tasks/types/')
      setTaskTypes(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching task types:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setSelectedTaskType(null)
    setIsModalOpen(true)
  }

  const handleEdit = (taskType) => {
    setSelectedTaskType(taskType)
    setIsModalOpen(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this task type?')) return

    try {
      await api.delete(`/tasks/types/${id}/`)
      fetchTaskTypes()
    } catch (error) {
      alert(
        'Error deleting task type: ' +
          (error.response?.data?.error || error.response?.data?.detail || error.message)
      )
    }
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setSelectedTaskType(null)
    fetchTaskTypes()
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Task Types</h1>
        {hasPermission('tasks', 'manage') && (
          <button
            onClick={handleCreate}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Task Type
          </button>
        )}
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      ) : taskTypes.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No task types found</div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tasks
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {taskTypes.map((taskType) => (
                <tr key={taskType.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{taskType.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        taskType.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {taskType.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{taskType.task_count || 0}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">
                      {new Date(taskType.created_at).toLocaleDateString()}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    {hasPermission('tasks', 'manage') && (
                      <>
                        <button
                          onClick={() => handleEdit(taskType)}
                          className="text-blue-600 hover:text-blue-900 mr-4"
                        >
                          <PencilIcon className="h-5 w-5 inline" />
                        </button>
                        <button
                          onClick={() => handleDelete(taskType.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <TrashIcon className="h-5 w-5 inline" />
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {isModalOpen && (
        <TaskTypeModal taskType={selectedTaskType} onClose={handleModalClose} />
      )}
    </div>
  )
}

export default TaskTypes
