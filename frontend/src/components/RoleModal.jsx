import { useState, useEffect } from 'react'
import api from '../services/api'
import { XMarkIcon } from '@heroicons/react/24/outline'

const MODULES = ['clients'] // Can be extended with more modules
const LEVELS = [
  { value: 'read', label: 'Read' },
  { value: 'create', label: 'Create' },
  { value: 'edit', label: 'Edit' },
  { value: 'manage', label: 'Manage' },
  { value: 'admin', label: 'Admin' },
]
const OWNERSHIP_TYPES = [
  { value: 'self', label: 'Self' },
  { value: 'group', label: 'Group' },
]

function RoleModal({ role, onClose }) {
  const [formData, setFormData] = useState({
    name: '',
    is_active: true,
    users: [],
    permissions: {},
  })
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchUsers()
    if (role) {
      setFormData({
        name: role.name || '',
        is_active: role.is_active ?? true,
        users: role.users || [],
        permissions: role.permissions || {},
      })
    } else {
      // Initialize permissions for all modules
      const initialPermissions = {}
      MODULES.forEach((module) => {
        initialPermissions[module] = {
          ownership: 'self',
          level: 'read',
          special: [],
        }
      })
      setFormData((prev) => ({ ...prev, permissions: initialPermissions }))
    }
  }, [role])

  const fetchUsers = async () => {
    try {
      const response = await api.get('/auth/users/')
      setUsers(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching users:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      if (role) {
        await api.patch(`/auth/roles/${role.id}/`, formData)
      } else {
        await api.post('/auth/roles/', formData)
      }
      onClose()
    } catch (error) {
      setError(error.response?.data?.error || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }))
  }

  const handlePermissionChange = (module, field, value) => {
    setFormData((prev) => ({
      ...prev,
      permissions: {
        ...prev.permissions,
        [module]: {
          ...prev.permissions[module],
          [field]: value,
        },
      },
    }))
  }

  const handleMultiSelect = (value) => {
    setFormData((prev) => ({
      ...prev,
      users: prev.users.includes(value)
        ? prev.users.filter((id) => id !== value)
        : [...prev.users, value],
    }))
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-10 mx-auto p-5 border w-11/12 md:w-4/5 lg:w-2/3 shadow-lg rounded-md bg-white max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold">
            {role ? 'Edit Role' : 'Create Role'}
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
              name="name"
              value={formData.name}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                name="is_active"
                checked={formData.is_active}
                onChange={handleChange}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Active</span>
            </label>
          </div>

          {/* Permissions */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Permissions
            </label>
            <div className="space-y-4 border border-gray-300 rounded-md p-4">
              {MODULES.map((module) => (
                <div key={module} className="border-b border-gray-200 pb-4 last:border-b-0 last:pb-0">
                  <h4 className="font-medium text-gray-900 mb-3 capitalize">{module}</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Ownership
                      </label>
                      <select
                        value={formData.permissions[module]?.ownership || 'self'}
                        onChange={(e) =>
                          handlePermissionChange(module, 'ownership', e.target.value)
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
                      >
                        {OWNERSHIP_TYPES.map((type) => (
                          <option key={type.value} value={type.value}>
                            {type.label}
                          </option>
                        ))}
                      </select>
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-gray-700 mb-1">
                        Level
                      </label>
                      <select
                        value={formData.permissions[module]?.level || 'read'}
                        onChange={(e) =>
                          handlePermissionChange(module, 'level', e.target.value)
                        }
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-sm"
                      >
                        {LEVELS.map((level) => (
                          <option key={level.value} value={level.value}>
                            {level.label}
                          </option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Users
            </label>
            <div className="max-h-48 overflow-y-auto border border-gray-300 rounded-md p-2">
              {users.map((user) => (
                <label key={user.id} className="flex items-center py-1">
                  <input
                    type="checkbox"
                    checked={formData.users.includes(user.id)}
                    onChange={() => handleMultiSelect(user.id)}
                    className="mr-2"
                  />
                  <span className="text-sm">
                    {user.first_name} {user.last_name} ({user.email})
                  </span>
                </label>
              ))}
            </div>
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
              {loading ? 'Saving...' : role ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default RoleModal
