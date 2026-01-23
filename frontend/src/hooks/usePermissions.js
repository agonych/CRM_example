import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

export function usePermissions() {
  const { user, isAdmin } = useAuth()
  const [permissions, setPermissions] = useState({})
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (isAdmin) {
      // Admins have all permissions
      setPermissions({
        clients: { read: true, create: true, edit: true, manage: true, admin: true },
        users: { read: true, create: true, edit: true, manage: true, admin: true },
        groups: { read: true, create: true, edit: true, manage: true, admin: true },
        roles: { read: true, create: true, edit: true, manage: true, admin: true },
      })
      setLoading(false)
      return
    }

    if (!user) {
      setLoading(false)
      return
    }

    // Fetch user's roles and calculate permissions
    const fetchPermissions = async () => {
      try {
        const response = await api.get('/auth/users/me/')
        const userData = response.data
        
        // Calculate permissions from roles
        const perms = {}
        if (userData.roles && Array.isArray(userData.roles)) {
          // Fetch role details to get permissions
          for (const roleId of userData.roles) {
            try {
              const roleResponse = await api.get(`/roles/${roleId}/`)
              const role = roleResponse.data
              
              if (role.permissions && Array.isArray(role.permissions)) {
                for (const perm of role.permissions) {
                  if (!perm.is_active) continue
                  
                  const module = perm.module_name
                  if (!perms[module]) {
                    perms[module] = {}
                  }
                  
                  // Track highest level for each ownership type
                  const key = `${perm.ownership_type}_${perm.level}`
                  if (!perms[module][key] || getLevelIndex(perm.level) > getLevelIndex(perms[module][key].level)) {
                    perms[module][key] = {
                      ownership_type: perm.ownership_type,
                      level: perm.level,
                    }
                  }
                }
              }
            } catch (error) {
              console.error(`Error fetching role ${roleId}:`, error)
            }
          }
        }
        
        // Convert to simple permission check format
        const simplePerms = {}
        for (const [module, modulePerms] of Object.entries(perms)) {
          simplePerms[module] = {
            read: hasLevel(modulePerms, 'read'),
            create: hasLevel(modulePerms, 'create'),
            edit: hasLevel(modulePerms, 'edit'),
            manage: hasLevel(modulePerms, 'manage'),
            admin: hasLevel(modulePerms, 'admin'),
          }
        }
        
        setPermissions(simplePerms)
      } catch (error) {
        console.error('Error fetching permissions:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchPermissions()
  }, [user, isAdmin])

  const hasPermission = (module, level = 'read') => {
    if (isAdmin) return true
    if (!permissions[module]) return false
    
    const modulePerms = permissions[module]
    const levelIndex = getLevelIndex(level)
    
    // Check if user has this level or higher
    const levels = ['read', 'create', 'edit', 'manage', 'admin']
    for (let i = levelIndex; i < levels.length; i++) {
      if (modulePerms[levels[i]]) {
        return true
      }
    }
    
    return false
  }

  return { permissions, hasPermission, loading }
}

function getLevelIndex(level) {
  const levels = ['read', 'create', 'edit', 'manage', 'admin']
  return levels.indexOf(level)
}

function hasLevel(modulePerms, level) {
  const levelIndex = getLevelIndex(level)

  // Check all ownership types
  for (const key of Object.keys(modulePerms)) {
    const perm = modulePerms[key]
    const permLevelIndex = getLevelIndex(perm.level)
    if (permLevelIndex >= levelIndex) {
      return true
    }
  }
  
  return false
}
