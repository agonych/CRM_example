import { useState, useEffect } from 'react'
import api from '../services/api'
import { useAuth } from '../contexts/AuthContext'
import { usePermissions } from '../hooks/usePermissions'
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'
import TaskModal from '../components/TaskModal'

function TaskBatchModal({ taskTypes, onSubmit, onClose }) {
  const [value, setValue] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSubmit = async () => {
    setLoading(true)
    await onSubmit(value)
    setLoading(false)
  }

  const options = taskTypes.filter((t) => t.is_active)

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold">Set Task Type</h3>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <XMarkIcon className="h-6 w-6" />
          </button>
        </div>

        <select
          value={value}
          onChange={(e) => setValue(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Select...</option>
          {options.map((item) => (
            <option key={item.id} value={item.id}>{item.name}</option>
          ))}
        </select>

        <div className="flex justify-end space-x-3 mt-4">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading || !value}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Applying...' : 'Apply'}
          </button>
        </div>
      </div>
    </div>
  )
}

function Tasks() {
  const { user } = useAuth()
  const { hasPermission } = usePermissions()
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedTask, setSelectedTask] = useState(null)
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [activeTab, setActiveTab] = useState('active')
  const [filterType, setFilterType] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [filterGroup, setFilterGroup] = useState('')
  const [taskTypes, setTaskTypes] = useState([])
  const [groups, setGroups] = useState([])
  const [selectedIds, setSelectedIds] = useState(new Set())
  const [batchAction, setBatchAction] = useState(null)

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
    fetchGroups()
  }, [])

  useEffect(() => {
    fetchTasks()
  }, [currentPage, activeTab, filterType, filterStatus, filterGroup])

  // Clear selection when page/filters change
  useEffect(() => {
    setSelectedIds(new Set())
  }, [currentPage, activeTab, filterType, filterStatus, filterGroup])

  const fetchTaskTypes = async () => {
    try {
      const response = await api.get('/tasks/types/')
      setTaskTypes(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching task types:', error)
    }
  }

  const fetchGroups = async () => {
    try {
      const response = await api.get('/groups/')
      setGroups(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching groups:', error)
    }
  }

  const fetchTasks = async () => {
    try {
      setLoading(true)
      const params = { page: currentPage }
      if (activeTab === 'active') {
        params.status = 'active'
      } else if (filterStatus) {
        params.status = filterStatus
      } else {
        params.status = 'completed,cancelled'
      }
      if (filterType) params.task_type = filterType
      if (filterGroup) params.group = filterGroup
      const response = await api.get('/tasks/', { params })
      setTasks(response.data.results || response.data)
      if (response.data.count !== undefined) {
        setTotalPages(Math.ceil(response.data.count / 20))
      }
    } catch (error) {
      console.error('Error fetching tasks:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreate = () => {
    setSelectedTask(null)
    setIsModalOpen(true)
  }

  const handleEdit = (task) => {
    setSelectedTask(task)
    setIsModalOpen(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return

    try {
      await api.delete(`/tasks/${id}/`)
      fetchTasks()
    } catch (error) {
      alert('Error deleting task: ' + (error.response?.data?.error || error.message))
    }
  }

  const handleComplete = async (task) => {
    try {
      await api.patch(`/tasks/${task.id}/`, { status: 'completed' })
      fetchTasks()
    } catch (error) {
      alert('Error completing task: ' + (error.response?.data?.error || error.message))
    }
  }

  const handleCancel = async (task) => {
    try {
      await api.patch(`/tasks/${task.id}/`, { status: 'cancelled' })
      fetchTasks()
    } catch (error) {
      alert('Error cancelling task: ' + (error.response?.data?.error || error.message))
    }
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setSelectedTask(null)
    fetchTasks()
  }

  const handleTabChange = (tab) => {
    setActiveTab(tab)
    setCurrentPage(1)
    setFilterStatus('')
  }

  const handleFilterChange = (setter) => (e) => {
    setter(e.target.value)
    setCurrentPage(1)
  }

  const toggleSelect = (id) => {
    setSelectedIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) {
        next.delete(id)
      } else {
        next.add(id)
      }
      return next
    })
  }

  const toggleSelectAll = () => {
    if (selectedIds.size === filteredTasks.length) {
      setSelectedIds(new Set())
    } else {
      setSelectedIds(new Set(filteredTasks.map((t) => t.id)))
    }
  }

  const handleBatchAction = async (actionName, value) => {
    try {
      await api.post('/tasks/batch/', {
        task_ids: Array.from(selectedIds),
        action: actionName,
        value: value || null,
      })
      setSelectedIds(new Set())
      fetchTasks()
    } catch (error) {
      alert('Batch action failed: ' + (error.response?.data?.error || error.message))
    }
  }

  const handleBatchModalSubmit = async (value) => {
    await handleBatchAction(batchAction, value)
    setBatchAction(null)
  }

  const filteredTasks = tasks.filter((task) => {
    if (!searchTerm) return true
    const searchLower = searchTerm.toLowerCase()
    return (
      task.name?.toLowerCase().includes(searchLower) ||
      task.description?.toLowerCase().includes(searchLower) ||
      task.client_detail?.first_name?.toLowerCase().includes(searchLower) ||
      task.client_detail?.last_name?.toLowerCase().includes(searchLower) ||
      task.task_type_detail?.name?.toLowerCase().includes(searchLower)
    )
  })

  const getStatusBadge = (status) => {
    const styles = {
      active: 'bg-blue-100 text-blue-800',
      completed: 'bg-green-100 text-green-800',
      cancelled: 'bg-gray-100 text-gray-800',
    }
    return (
      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${styles[status] || styles.active}`}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    )
  }

  const formatDuration = (minutes) => {
    if (minutes < 60) return `${minutes}m`
    const h = Math.floor(minutes / 60)
    const m = minutes % 60
    return m > 0 ? `${h}h ${m}m` : `${h}h`
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
        {hasPermission('tasks', 'create') && (
          <button
            onClick={handleCreate}
            className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Add Task
          </button>
        )}
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          <button
            onClick={() => handleTabChange('active')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'active'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Active Tasks
          </button>
          <button
            onClick={() => handleTabChange('history')}
            className={`py-2 px-1 border-b-2 font-medium text-sm ${
              activeTab === 'history'
                ? 'border-blue-500 text-blue-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            Task History
          </button>
        </nav>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 flex flex-wrap gap-4">
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search tasks..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md leading-5 bg-white placeholder-gray-500 focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            />
          </div>
        </div>
        <div className="w-48">
          <select
            value={filterType}
            onChange={handleFilterChange(setFilterType)}
            className="block w-full py-2 px-3 border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="">All Types</option>
            {taskTypes.filter((t) => t.is_active).map((t) => (
              <option key={t.id} value={t.id}>{t.name}</option>
            ))}
          </select>
        </div>
        <div className="w-48">
          <select
            value={filterGroup}
            onChange={handleFilterChange(setFilterGroup)}
            className="block w-full py-2 px-3 border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
          >
            <option value="">All Groups</option>
            {groups.map((g) => (
              <option key={g.id} value={g.id}>{g.name}</option>
            ))}
          </select>
        </div>
        {activeTab === 'history' && (
          <div className="w-48">
            <select
              value={filterStatus}
              onChange={handleFilterChange(setFilterStatus)}
              className="block w-full py-2 px-3 border border-gray-300 rounded-md bg-white focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
            >
              <option value="">All Statuses</option>
              <option value="completed">Completed</option>
              <option value="cancelled">Cancelled</option>
            </select>
          </div>
        )}
      </div>

      {/* Batch Action Bar */}
      {selectedIds.size > 0 && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-md flex items-center flex-wrap gap-2">
          <span className="text-sm font-medium text-blue-800 mr-2">
            {selectedIds.size} selected
          </span>
          {activeTab === 'active' && (
            <>
              <button
                onClick={() => handleBatchAction('complete')}
                className="px-3 py-1.5 text-sm bg-green-600 text-white rounded-md hover:bg-green-700"
              >
                Complete
              </button>
              <button
                onClick={() => handleBatchAction('cancel')}
                className="px-3 py-1.5 text-sm bg-orange-600 text-white rounded-md hover:bg-orange-700"
              >
                Cancel
              </button>
            </>
          )}
          <button
            onClick={() => setBatchAction('set_type')}
            className="px-3 py-1.5 text-sm bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Set Type
          </button>
          <button
            onClick={() => setSelectedIds(new Set())}
            className="ml-auto px-3 py-1.5 text-sm text-gray-600 hover:text-gray-800"
          >
            Clear Selection
          </button>
        </div>
      )}

      {/* Tasks Table */}
      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      ) : filteredTasks.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          No tasks found
        </div>
      ) : (
        <>
          <div className="bg-white shadow overflow-hidden sm:rounded-md">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 w-10">
                    <input
                      type="checkbox"
                      checked={selectedIds.size === filteredTasks.length && filteredTasks.length > 0}
                      onChange={toggleSelectAll}
                      className="rounded border-gray-300"
                    />
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Task
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Client
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Type
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Assigned To
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Due Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Value
                  </th>
                  {activeTab === 'history' && (
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                  )}
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredTasks.map((task) => (
                  <tr key={task.id} className={`hover:bg-gray-50 ${selectedIds.has(task.id) ? 'bg-blue-50' : ''}`}>
                    <td className="px-4 py-4 w-10">
                      <input
                        type="checkbox"
                        checked={selectedIds.has(task.id)}
                        onChange={() => toggleSelect(task.id)}
                        className="rounded border-gray-300"
                      />
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm font-medium text-gray-900">{task.name}</div>
                      {task.description && (
                        <div className="text-xs text-gray-500 truncate max-w-xs">
                          {task.description}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">
                        {task.client_detail
                          ? `${task.client_detail.first_name} ${task.client_detail.last_name}`
                          : '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {task.task_type_detail?.name || '-'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {task.assigned_to_detail
                          ? `${task.assigned_to_detail.first_name} ${task.assigned_to_detail.last_name}`
                          : 'Unassigned'}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {new Date(task.due_date).toLocaleString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {formatDuration(task.duration)}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-500">
                        {task.monetary_value > 0
                          ? `$${task.monetary_value.toFixed(2)}`
                          : '-'}
                      </div>
                    </td>
                    {activeTab === 'history' && (
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getStatusBadge(task.status)}
                      </td>
                    )}
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      {task.status === 'active' && hasPermission('tasks', 'edit') && (
                        <>
                          <button
                            onClick={() => handleComplete(task)}
                            className="text-green-600 hover:text-green-900 mr-3"
                            title="Mark Complete"
                          >
                            <CheckCircleIcon className="h-5 w-5 inline" />
                          </button>
                          <button
                            onClick={() => handleCancel(task)}
                            className="text-orange-600 hover:text-orange-900 mr-3"
                            title="Cancel Task"
                          >
                            <XCircleIcon className="h-5 w-5 inline" />
                          </button>
                        </>
                      )}
                      {hasPermission('tasks', 'edit') && (
                        <button
                          onClick={() => handleEdit(task)}
                          className="text-blue-600 hover:text-blue-900 mr-3"
                        >
                          <PencilIcon className="h-5 w-5 inline" />
                        </button>
                      )}
                      {hasPermission('tasks', 'manage') && (
                        <button
                          onClick={() => handleDelete(task.id)}
                          className="text-red-600 hover:text-red-900"
                        >
                          <TrashIcon className="h-5 w-5 inline" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="mt-4 flex justify-center">
              <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                <button
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  Previous
                </button>
                <span className="relative inline-flex items-center px-4 py-2 border border-gray-300 bg-white text-sm font-medium text-gray-700">
                  Page {currentPage} of {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50"
                >
                  Next
                </button>
              </nav>
            </div>
          )}
        </>
      )}

      {/* Task Modal */}
      {isModalOpen && (
        <TaskModal
          task={selectedTask}
          onClose={handleModalClose}
        />
      )}

      {/* Batch Action Modal */}
      {batchAction && (
        <TaskBatchModal
          taskTypes={taskTypes}
          onSubmit={handleBatchModalSubmit}
          onClose={() => setBatchAction(null)}
        />
      )}
    </div>
  )
}

export default Tasks
