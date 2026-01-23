import { useState, useEffect } from 'react'
import api from '../services/api'
import { XMarkIcon, PlusIcon, TrashIcon } from '@heroicons/react/24/outline'

function RoleModal({ role, onClose }) {
  const [formData, setFormData] = useState({
    name: '',
    is_active: true,
    users: [],
  })
  const [permissions, setPermissions] = useState([])
  const [availablePermissions, setAvailablePermissions] = useState({})
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchUsers()
    fetchAvailablePermissions()
    if (role) {
      setFormData({
        name: role.name || '',
        is_active: role.is_active ?? true,
        users: role.users || [],
      })
      // Load existing permissions
      if (role.permissions && Array.isArray(role.permissions)) {
        setPermissions(role.permissions.map(p => ({
          id: p.id,
          module_name: p.module_name,
          ownership_type: p.ownership_type,
          level: p.level,
          is_active: p.is_active ?? true,
        })))
      }
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

  const fetchAvailablePermissions = async () => {
    try {
      const response = await api.get('/permissions/available/')
      setAvailablePermissions(response.data)
    } catch (error) {
      console.error('Error fetching available permissions:', error)
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const roleData = { ...formData }
      
      if (role) {
        // Update role
        await api.patch(`/roles/${role.id}/`, roleData)
        
        // Update permissions
        const existingPermIds = permissions.filter(p => p.id).map(p => p.id)
        const currentPerms = role.permissions || []
        const currentPermIds = currentPerms.map(p => p.id)
        
        // Delete removed permissions
        const toDelete = currentPermIds.filter(id => !existingPermIds.includes(id))
        for (const id of toDelete) {
          await api.delete(`/roles/permissions/${id}/`)
        }
        
        // Create/update permissions
        for (const perm of permissions) {
          const permData = {
            module_name: perm.module_name,
            ownership_type: perm.ownership_type,
            level: perm.level,
            is_active: perm.is_active,
          }
          
          if (perm.id) {
            await api.patch(`/roles/permissions/${perm.id}/`, permData)
          } else {
            await api.post('/roles/permissions/', { role: role.id, ...permData })
          }
        }
      } else {
        // Create role
        const response = await api.post('/roles/', roleData)
        const newRole = response.data
        
        // Create permissions
        for (const perm of permissions) {
          await api.post('/roles/permissions/', {
            role: newRole.id,
            module_name: perm.module_name,
            ownership_type: perm.ownership_type,
            level: perm.level,
            is_active: perm.is_active,
          })
        }
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

  const handleMultiSelect = (value) => {
    setFormData((prev) => ({
      ...prev,
      users: prev.users.includes(value)
        ? prev.users.filter((id) => id !== value)
        : [...prev.users, value],
    }))
  }

  const addPermission = () => {
    const modules = Object.keys(availablePermissions)
    if (modules.length === 0) return
    
    const firstModule = modules[0]
    const modulePerms = availablePermissions[firstModule]
    
    setPermissions([...permissions, {
      id: null,
      module_name: firstModule,
      ownership_type: modulePerms.types[0] || 'self',
      level: modulePerms.levels[0] || 'read',
      is_active: true,
    }])
  }

  const removePermission = (index) => {
    setPermissions(permissions.filter((_, i) => i !== index))
  }

  const updatePermission = (index, field, value) => {
    const updated = [...permissions]
    updated[index] = { ...updated[index], [field]: value }
    setPermissions(updated)
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
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Permissions
              </label>
              <button
                type="button"
                onClick={addPermission}
                className="flex items-center px-2 py-1 text-sm bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                <PlusIcon className="h-4 w-4 mr-1" />
                Add Permission
              </button>
            </div>
            <div className="space-y-2 border border-gray-300 rounded-md p-4">
              {permissions.length === 0 ? (
                <p className="text-sm text-gray-500 text-center py-4">
                  No permissions added. Click "Add Permission" to add one.
                </p>
              ) : (
                permissions.map((perm, index) => {
                  const modulePerms = availablePermissions[perm.module_name] || { types: [], levels: [] }
                  return (
                    <div key={index} className="flex items-center gap-2 p-2 bg-gray-50 rounded border">
                      <div className="flex-1 grid grid-cols-3 gap-2">
                        <select
                          value={perm.module_name}
                          onChange={(e) => updatePermission(index, 'module_name', e.target.value)}
                          className="px-2 py-1 border border-gray-300 rounded text-sm"
                        >
                          {Object.keys(availablePermissions).map(module => (
                            <option key={module} value={module}>{module}</option>
                          ))}
                        </select>
                        <select
                          value={perm.ownership_type}
                          onChange={(e) => updatePermission(index, 'ownership_type', e.target.value)}
                          className="px-2 py-1 border border-gray-300 rounded text-sm"
                        >
                          {modulePerms.types.map(type => (
                            <option key={type} value={type}>{type}</option>
                          ))}
                        </select>
                        <select
                          value={perm.level}
                          onChange={(e) => updatePermission(index, 'level', e.target.value)}
                          className="px-2 py-1 border border-gray-300 rounded text-sm"
                        >
                          {modulePerms.levels.map(level => (
                            <option key={level} value={level}>{level}</option>
                          ))}
                        </select>
                      </div>
                      <button
                        type="button"
                        onClick={() => removePermission(index)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <TrashIcon className="h-5 w-5" />
                      </button>
                    </div>
                  )
                })
              )}
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
