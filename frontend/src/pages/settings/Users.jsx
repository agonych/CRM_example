import { useState, useEffect } from 'react'
import api from '../../services/api'
import { useAuth } from '../../contexts/AuthContext'
import { usePermissions } from '../../hooks/usePermissions'
import {
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
} from '@heroicons/react/24/outline'
import UserModal from '../../components/UserModal'

function Users() {
  const { isAdmin } = useAuth()
  const { loading: permissionsLoading, permissions } = usePermissions()
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [selectedUser, setSelectedUser] = useState(null)
  const [search, setSearch] = useState('')
  const [filterGroup, setFilterGroup] = useState('')
  const [filterRole, setFilterRole] = useState('')
  const [filterType, setFilterType] = useState('')
  const [activeTab, setActiveTab] = useState('active')
  const [groups, setGroups] = useState([])
  const [roles, setRoles] = useState([])

  useEffect(() => {
    // Wait for permissions to load, then check and fetch
    if (permissionsLoading) {
      return
    }
    
    const canRead = isAdmin || (permissions.users && permissions.users.read)
    
    if (canRead) {
      fetchUsers()
      fetchGroups()
      fetchRoles()
    } else {
      setLoading(false)
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAdmin, permissionsLoading, permissions?.users?.read])

  const fetchUsers = async () => {
    try {
      setLoading(true)
      setError(null)
      const params = {}
      params.is_active = activeTab === 'active' ? 'true' : 'false'
      if (search) params.search = search
      if (filterGroup) params.group = filterGroup
      if (filterRole) params.role = filterRole
      if (filterType) params.user_type = filterType
      const response = await api.get('/auth/users/', { params })
      setUsers(response.data.results || response.data)
    } catch (error) {
      console.error('Error fetching users:', error)
      console.error('Error details:', error.response?.data || error.message)
      setError(error.response?.data?.error || error.message || 'Failed to load users')
      // Set empty array on error so UI shows error message
      setUsers([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchUsers()
  }, [search, filterGroup, filterRole, filterType, activeTab])

  const fetchGroups = async () => {
    try {
      const response = await api.get('/groups/')
      setGroups(response.data.results || response.data)
    } catch (err) {
      console.error('Error fetching groups:', err)
    }
  }

  const fetchRoles = async () => {
    try {
      const response = await api.get('/roles/')
      setRoles(response.data.results || response.data)
    } catch (err) {
      console.error('Error fetching roles:', err)
    }
  }

  const handleCreate = () => {
    setSelectedUser(null)
    setIsModalOpen(true)
  }

  const handleEdit = (user) => {
    setSelectedUser(user)
    setIsModalOpen(true)
  }

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this user?')) {
      return
    }

    try {
      await api.delete(`/auth/users/${id}/`)
      fetchUsers()
    } catch (error) {
      alert('Error deleting user: ' + (error.response?.data?.error || error.message))
    }
  }

  const handleModalClose = () => {
    setIsModalOpen(false)
    setSelectedUser(null)
    fetchUsers()
  }

  // Show loading while permissions are loading
  if (permissionsLoading) {
    return (
      <div className="text-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
      </div>
    )
  }
  
  const canRead = isAdmin || (permissions.users && permissions.users.read)
  if (!canRead) {
    return (
      <div className="text-center py-12 text-gray-500">
        You do not have permission to access this page.
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Users</h1>
        <button
          onClick={handleCreate}
          className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          <PlusIcon className="h-5 w-5 mr-2" />
          Add User
        </button>
      </div>

      <div className="mb-4 border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {['active', 'inactive'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === tab
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              {tab === 'active' ? 'Active Users' : 'Inactive Users'}
            </button>
          ))}
        </nav>
      </div>

      <div className="mb-4 flex flex-wrap gap-4">
        <div className="relative flex-1 min-w-[200px]">
          <MagnifyingGlassIcon className="h-5 w-5 absolute left-3 top-2.5 text-gray-400" />
          <input
            type="text"
            placeholder="Search by name..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <select
          value={filterGroup}
          onChange={(e) => setFilterGroup(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Groups</option>
          {groups.map((g) => (
            <option key={g.id} value={g.id}>{g.name}</option>
          ))}
        </select>
        <select
          value={filterRole}
          onChange={(e) => setFilterRole(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Roles</option>
          {roles.map((r) => (
            <option key={r.id} value={r.id}>{r.name}</option>
          ))}
        </select>
        <select
          value={filterType}
          onChange={(e) => setFilterType(e.target.value)}
          className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">All Types</option>
          <option value="user">Users</option>
          <option value="admin">Admins</option>
        </select>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <div className="bg-red-50 border border-red-200 rounded-md p-4 max-w-md mx-auto">
            <p className="text-red-800 font-medium">Error loading users</p>
            <p className="text-red-600 text-sm mt-1">{error}</p>
            <button
              onClick={fetchUsers}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 text-sm"
            >
              Retry
            </button>
          </div>
        </div>
      ) : users.length === 0 ? (
        <div className="text-center py-12 text-gray-500">No users found</div>
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Email
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Role
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Groups
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Clients
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tasks
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">
                      {user.first_name} {user.last_name}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{user.email}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span
                      className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        user.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}
                    >
                      {user.is_active ? 'Active' : 'Inactive'}
                    </span>
                    {user.is_superuser && (
                      <span className="ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full bg-blue-100 text-blue-800">
                        Admin
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-500">
                      {user.role_names?.length > 0
                        ? user.role_names.join(', ')
                        : '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-gray-500">
                      {user.group_names?.length > 0
                        ? user.group_names.join(', ')
                        : '-'}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{user.assigned_clients_count || 0}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm text-gray-500">{user.assigned_tasks_count || 0}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <button
                      onClick={() => handleEdit(user)}
                      className="text-blue-600 hover:text-blue-900 mr-4"
                    >
                      <PencilIcon className="h-5 w-5 inline" />
                    </button>
                    <button
                      onClick={() => handleDelete(user.id)}
                      className="text-red-600 hover:text-red-900"
                    >
                      <TrashIcon className="h-5 w-5 inline" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {isModalOpen && (
        <UserModal user={selectedUser} onClose={handleModalClose} />
      )}
    </div>
  )
}

export default Users
