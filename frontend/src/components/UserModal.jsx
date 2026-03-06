import { useState, useEffect } from 'react'
import api from '../services/api'
import { XMarkIcon } from '@heroicons/react/24/outline'

function UserModal({ user, onClose }) {
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    password2: '',
    is_active: true,
    is_superuser: false,
    groups: [],
  })
  const [groups, setGroups] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchGroups()
    if (user) {
      setFormData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        email: user.email || '',
        password: '',
        password2: '',
        is_active: user.is_active ?? true,
        is_superuser: user.is_superuser ?? false,
        groups: user.groups || [],
      })
    }
  }, [user])

  const fetchGroups = async () => {
    try {
      const response = await api.get('/groups/')
      setGroups(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching groups:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!user && formData.password !== formData.password2) {
      setError('Passwords do not match')
      return
    }

    if (!user && !formData.password) {
      setError('Password is required for new users')
      return
    }

    setLoading(true)

    try {
      const data = { ...formData }
      if (user && !data.password) {
        delete data.password
        delete data.password2
      } else {
        delete data.password2
      }

      if (user) {
        await api.patch(`/auth/users/${user.id}/`, data)
      } else {
        await api.post('/auth/users/register/', data)
      }
      onClose()
    } catch (error) {
      setError(error.response?.data?.error || error.response?.data?.password?.[0] || 'An error occurred')
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

  const handleMultiSelect = (value) => {
    setFormData((prev) => ({
      ...prev,
      groups: prev.groups.includes(value)
        ? prev.groups.filter((id) => id !== value)
        : [...prev.groups, value],
    }))
  }

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
      <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-bold">
            {user ? 'Edit User' : 'Create User'}
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
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                First Name *
              </label>
              <input
                type="text"
                name="first_name"
                value={formData.first_name}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Last Name *
              </label>
              <input
                type="text"
                name="last_name"
                value={formData.last_name}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email *
            </label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Password {user ? '(leave blank to keep current)' : '*'}
              </label>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required={!user}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            {!user && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Confirm Password *
                </label>
                <input
                  type="password"
                  name="password2"
                  value={formData.password2}
                  onChange={handleChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            )}
          </div>

          <div className="space-y-2">
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
            <label className="flex items-center">
              <input
                type="checkbox"
                name="is_superuser"
                checked={formData.is_superuser}
                onChange={handleChange}
                className="mr-2"
              />
              <span className="text-sm text-gray-700">Admin</span>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Groups
            </label>
            <div className="max-h-32 overflow-y-auto border border-gray-300 rounded-md p-2">
              {groups.map((group) => (
                <label key={group.id} className="flex items-center py-1">
                  <input
                    type="checkbox"
                    checked={formData.groups.includes(group.id)}
                    onChange={() => handleMultiSelect(group.id)}
                    className="mr-2"
                  />
                  <span className="text-sm">{group.name}</span>
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
              {loading ? 'Saving...' : user ? 'Update' : 'Create'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

export default UserModal
